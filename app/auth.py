import os
import time
import requests
from dotenv import load_dotenv, set_key

# Cargar variables de entorno iniciales
load_dotenv()

ENV_FILE = ".env"

def get_env_var(var_name):
    # Recargar para asegurar que tenemos los ultimos valores si fueron actualizados
    load_dotenv(override=True)
    return os.getenv(var_name)

def update_env_file(key, value):
    # Actualiza el archivo .env y la variable de entorno en memoria
    set_key(ENV_FILE, key, value)
    os.environ[key] = value

def refresh_tokens():
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
        print(f"Refrescando token...")
        response = requests.get(token_url, params=params)
        response.raise_for_status()
        data = response.json()

        new_access_token = data["access_token"]
        new_refresh_token = data["refresh_token"]
        
        # Guardar nuevos tokens
        update_env_file("ACCESS_TOKEN", new_access_token)
        update_env_file("REFRESH_TOKEN", new_refresh_token)
        
        print("Token refrescado exitosamente.")
        return new_access_token

    except requests.exceptions.RequestException as e:
        print(f"Error al refrescar token: {e}")
        if response.text:
            print(f"Detalle: {response.text}")
        raise

def call_bitrix_method(method, params=None):
    """
    Llama a un método de la API de Bitrix24 manejando la autenticación y reintentos.
    """
    if params is None:
        params = {}

    domain = get_env_var("BITRIX_DOMAIN")
    access_token = get_env_var("ACCESS_TOKEN")
    
    if not domain or not access_token:
        raise ValueError("Faltan credenciales en .env (BITRIX_DOMAIN, ACCESS_TOKEN)")

    url = f"https://{domain}/rest/{method}"
    
    # Agregar auth al payload
    params["auth"] = access_token

    try:
        response = requests.post(url, json=params)
        
        # Si el token expiró (código 401 o error específico de Bitrix), refrescar y reintentar
        if response.status_code == 401 or (response.status_code == 200 and "expired_token" in response.text):
            print("Token expirado, intentando refrescar...")
            new_token = refresh_tokens()
            params["auth"] = new_token
            response = requests.post(url, json=params)

        response.raise_for_status()
        return response.json()

    except Exception as e:
        print(f"Error llamando a {method}: {e}")
        if 'response' in locals() and response is not None:
             print(f"Respuesta de Bitrix: {response.text}")
        raise
