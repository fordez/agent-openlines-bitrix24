"""
Módulo de autenticación y llamadas a la API de Bitrix24.
Usa httpx.AsyncClient para no bloquear el event loop.
"""
import os
import httpx
import sys
import os
import httpx
import sys

# BASE_DIR and ENV_FILE only used for local dev if they exist
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_FILE = os.path.join(BASE_DIR, ".env")

# Cliente HTTP compartido (reutiliza conexiones TCP)
_http_client: httpx.AsyncClient | None = None


async def get_http_client() -> httpx.AsyncClient:
    """Retorna un cliente HTTP singleton para reutilizar conexiones."""
    global _http_client
    if _http_client is None or _http_client.is_closed:
        _http_client = httpx.AsyncClient(timeout=30)
    return _http_client


def get_env_var(var_name):
    """Obtiene una variable de entorno, priorizando el entorno y limpiando comillas."""
    # Intentar obtener del entorno (que puede haber sido inyectado por docker-compose o actualizado en runtime)
    val = os.environ.get(var_name)
    if not val:
        # Fallback a os.getenv (que usa lo cargado por load_dotenv)
        val = os.getenv(var_name)
        
    if val:
        # Docker env_file carga valores literales incluyendo comillas si existen
        return str(val).strip("'\"")
    return val


def update_env_file(key, value):
    """Actualiza la variable en memoria. Si existe archivo .env local, lo actualiza también."""
    os.environ[key] = value
    if os.path.exists(ENV_FILE):
        try:
            from dotenv import set_key
            set_key(ENV_FILE, key, value)
        except Exception:
            pass





async def call_bitrix_method(method, params=None, access_token=None, domain=None, member_id=None):
    """
    Llama a un método de la API de Bitrix24.
    - Resolucion de tenant: Prioriza member_id -> context_var -> env.
    """
    if params is None:
        params = {}

    from app.token_manager import get_token_manager
    tm = await get_token_manager()

    # 1. Resolver member_id
    if not member_id:
        member_id = await tm.get_member_id()

    # 2. Obtener Token y Dominio si no se pasaron
    if not access_token:
        access_token = await tm.get_token(member_id)

    if not domain:
        # Intentar obtener del cache de Redis vía TokenManager para este tenant
        if member_id:
            redis = await tm._get_redis()
            cached_domain = await redis.get(tm._get_redis_key(member_id, "domain"))
            if cached_domain:
                domain = cached_domain.decode("utf-8") if isinstance(cached_domain, bytes) else cached_domain

        if not domain:
            domain = get_env_var("BITRIX_DOMAIN")

    if not domain or not access_token:
        error_msg = f"Faltan credenciales para tenant {member_id}: DOMAIN={'OK' if domain else 'MISSING'}, TOKEN={'OK' if access_token else 'MISSING'}"
        sys.stderr.write(f"  ❌ {error_msg}\n")
        raise ValueError(error_msg)

    url = f"https://{domain}/rest/{method}"
    # Se agrega auth como query param
    auth_url = f"{url}?auth={access_token}" if "?" not in url else f"{url}&auth={access_token}"

    try:
        client = await get_http_client()
        response = await client.post(auth_url, json=params)

        # Si el token es inválido o expiró
        if response.status_code in [400, 401]:
            try:
                data = response.json()
                if data.get("error") in ["expired_token", "invalid_token", "WRONG_AUTH_TYPE"]:
                    sys.stderr.write(f"  🔄 Token expirado para {member_id}, refrescando...\n")
                    new_token = await tm.force_refresh(member_id)
                    auth_url = f"{url}?auth={new_token}" if "?" not in url else f"{url}&auth={new_token}"
                    response = await client.post(auth_url, json=params)
            except:
                pass

        if response.status_code >= 400:
            sys.stderr.write(f"  ❌ Bitrix API Error ({member_id}): {response.text}\n")

        response.raise_for_status()
        return response.json()

    except Exception as e:
        sys.stderr.write(f"  ❌ Error llamando a {method}: {e}\n")
        raise

async def get_current_user_id() -> int:
    """Retorna el ID del usuario actual (el bot). Fallback a 1 (Daniel Posada) si falla."""
    try:
        res = await call_bitrix_method("user.current")
        user_id = res.get("result", {}).get("ID")
        if user_id:
            return int(user_id)
    except Exception as e:
        sys.stderr.write(f"  ⚠️ Error obteniendo user.current: {e}. Usando fallback ID=1\n")
    
    return int(os.getenv("DEFAULT_RESPONSIBLE_ID", 1))
