"""
Módulo de autenticación y llamadas a la API de Bitrix24.
Usa httpx.AsyncClient para no bloquear el event loop.
"""
import os
import httpx
from dotenv import load_dotenv, set_key

load_dotenv()

ENV_FILE = ".env"

# Cliente HTTP compartido (reutiliza conexiones TCP)
_http_client: httpx.AsyncClient | None = None


async def get_http_client() -> httpx.AsyncClient:
    """Retorna un cliente HTTP singleton para reutilizar conexiones."""
    global _http_client
    if _http_client is None or _http_client.is_closed:
        _http_client = httpx.AsyncClient(timeout=30)
    return _http_client


def get_env_var(var_name):
    """Obtiene una variable de entorno, limpiando posibles comillas de Docker."""
    val = os.getenv(var_name)
    if val:
        # Docker env_file carga valores literales incluyendo comillas si existen
        return val.strip("'\"")
    return val


def update_env_file(key, value):
    set_key(ENV_FILE, key, value)
    os.environ[key] = value


async def refresh_tokens():
    client_id = get_env_var("CLIENT_ID")
    client_secret = get_env_var("CLIENT_SECRET")
    refresh_token = get_env_var("REFRESH_TOKEN")

    if not client_id or not client_secret:
        raise ValueError("CLIENT_ID y CLIENT_SECRET son necesarios para refrescar el token.")

    token_url = "https://oauth.bitrix.info/oauth/token/"
    params = {
        "grant_type": "refresh_token",
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token,
    }

    try:
        print("Refrescando token...")
        client = await get_http_client()
        response = await client.get(token_url, params=params)
        response.raise_for_status()
        data = response.json()

        new_access_token = data["access_token"]
        new_refresh_token = data["refresh_token"]

        update_env_file("ACCESS_TOKEN", new_access_token)
        update_env_file("REFRESH_TOKEN", new_refresh_token)

        print("Token refrescado exitosamente.")
        return new_access_token

    except httpx.HTTPError as e:
        print(f"Error al refrescar token: {e}")
        raise


async def call_bitrix_method(method, params=None):
    """
    Llama a un método de la API de Bitrix24 de forma asíncrona.
    Maneja autenticación y reintentos por token expirado.
    """
    if params is None:
        params = {}

    domain = get_env_var("BITRIX_DOMAIN")
    access_token = get_env_var("ACCESS_TOKEN")

    if not domain or not access_token:
        raise ValueError("Faltan credenciales en .env (BITRIX_DOMAIN, ACCESS_TOKEN)")

    url = f"https://{domain}/rest/{method}"
    params["auth"] = access_token

    try:
        client = await get_http_client()
        response = await client.post(url, json=params)

        # Token expirado: refrescar y reintentar
        if response.status_code == 401 or (response.status_code == 200 and "expired_token" in response.text):
            print("Token expirado, intentando refrescar...")
            new_token = await refresh_tokens()
            params["auth"] = new_token
            response = await client.post(url, json=params)

        response.raise_for_status()
        return response.json()

    except Exception as e:
        print(f"Error llamando a {method}: {e}")
        raise
