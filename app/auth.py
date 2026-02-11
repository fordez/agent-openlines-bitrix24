"""
Módulo de autenticación y llamadas a la API de Bitrix24.
Usa httpx.AsyncClient para no bloquear el event loop.
"""
import os
import httpx
import sys
from dotenv import load_dotenv, set_key

# Cargar variables de entorno usando ruta absoluta para evitar fallos en subprocesos
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_FILE = os.path.join(BASE_DIR, ".env")
load_dotenv(ENV_FILE)

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
    set_key(ENV_FILE, key, value)
    os.environ[key] = value





async def call_bitrix_method(method, params=None, access_token=None, domain=None):
    """
    Llama a un método de la API de Bitrix24.
    - Si access_token está presente: lo usa (para respuestas a Bitrix desde eventos)
    - Si no: usa TOKEN MANAGER (para tools del MCP server)
    """
    if params is None:
        params = {}

    # Obtener dominio (prioritario: parámetro > env var)
    if not domain:
        domain = get_env_var("BITRIX_DOMAIN")
        if not domain:
            endpoint = get_env_var("BITRIX_CLIENT_ENDPOINT")
            if endpoint:
                domain = endpoint.replace("https://", "").split("/")[0]

    # Si NO se pasó token explícitamente, usar TokenManager
    if not access_token:
        from app.token_manager import get_token_manager
        token_manager = await get_token_manager()
        access_token = await token_manager.get_token()

    if not domain or not access_token:
        error_msg = f"Faltan credenciales: DOMAIN={'OK' if domain else 'MISSING'}, TOKEN={'OK' if access_token else 'MISSING'}"
        sys.stderr.write(f"  ❌ {error_msg}\n")
        # Debug: list available env vars starting with BITRIX or ACCESS
        relevant_vars = {k: v[:5] + "..." if v else v for k, v in os.environ.items() if "BITRIX" in k or "TOKEN" in k or "ENDPOINT" in k}
        sys.stderr.write(f"  🔍 Variables relevantes presentes: {relevant_vars}\n")
        raise ValueError(error_msg)

    url = f"https://{domain}/rest/{method}"

    # Append auth to URL as query param (safer for some Bitrix endpoints)
    if "?" in url:
        url += f"&auth={access_token}"
    else:
        url += f"?auth={access_token}"

    try:
        client = await get_http_client()
        response = await client.post(url, json=params)

        # Si el token es inválido o expiró (401/400 con error de auth)
        if response.status_code in [400, 401]:
            try:
                data = response.json()
                error_code = data.get("error", "")
                if error_code in ["expired_token", "invalid_token", "WRONG_AUTH_TYPE"]:
                    sys.stderr.write(f"  🔄 Token rechazado por Bitrix ({error_code}). Reintentando refresh...\n")
                    from app.token_manager import get_token_manager
                    tm = await get_token_manager()
                    await tm.force_refresh()
                    # Re-obtener URL con nuevo token
                    new_token = await tm.get_token()
                    new_url = url.split("?")[0] + f"?auth={new_token}"
                    response = await client.post(new_url, json=params)
            except:
                pass

        if response.status_code >= 400:
            sys.stderr.write(f"  ❌ Bitrix API Error Body: {response.text}\n")

        response.raise_for_status()
        data = response.json()
        sys.stderr.write(f"  📡 Bitrix API: {method} -> Result: {'Success' if 'result' in data else 'Error or Empty'}\n")
        if "error" in data:
            sys.stderr.write(f"  ⚠️ Bitrix API Error: {data.get('error_description', data.get('error'))}\n")
        return data

    except Exception as e:
        sys.stderr.write(f"  ❌ Error llamando a {method}: {e}\n")
        raise

async def get_current_user_id() -> int:
    """Retorna el ID del usuario actual (el bot). Hardcoded 3040 para pruebas."""
    return 3040
