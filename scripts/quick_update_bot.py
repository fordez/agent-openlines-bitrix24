
import os
import httpx
import asyncio
from dotenv import load_dotenv

async def main():
    load_dotenv()
    
    domain = os.getenv("BITRIX_DOMAIN")
    token = os.getenv("ACCESS_TOKEN")
    bot_code = os.getenv("BOT_CODE", "bot_viajes")
    webhook_url = os.getenv("WEBHOOK_HANDLER_URL")
    bot_name = os.getenv("BOT_NAME", "Bot Viajes")

    if not all([domain, token, webhook_url]):
        print("ERROR: Faltan variables en .env (BITRIX_DOMAIN, ACCESS_TOKEN, WEBHOOK_HANDLER_URL)")
        return

    # Limpiar comillas si existen (común en env_file de Docker)
    domain = domain.strip("'\"")
    token = token.strip("'\"")
    webhook_url = webhook_url.strip("'\"")

    print(f"Buscando bot '{bot_code}' en {domain}...")
    
    async with httpx.AsyncClient(timeout=30) as client:
        # 1. Función para refrescar el token
        async def refresh_token():
            print("Refrescando token...")
            client_id = os.getenv("CLIENT_ID").strip("'\"")
            client_secret = os.getenv("CLIENT_SECRET").strip("'\"")
            refresh_token = os.getenv("REFRESH_TOKEN").strip("'\"")
            token_url = "https://oauth.bitrix.info/oauth/token/"
            params = {
                "grant_type": "refresh_token",
                "client_id": client_id,
                "client_secret": client_secret,
                "refresh_token": refresh_token,
            }
            r = await client.post(token_url, params=params)
            if r.status_code == 200:
                data = r.json()
                new_access = data["access_token"]
                new_refresh = data["refresh_token"]
                print("Token refrescado exitosamente.")
                # Actualizar el archivo .env sería ideal pero para este script basta con devolver el nuevo access
                return new_access
            print(f"Error al refrescar token: {r.status_code} - {r.text}")
            return None

        # Función para llamar a la API con reintento por expiración
        async def call_api(method_url, payload=None):
            nonlocal token
            r = await client.post(method_url, json=payload)
            if r.status_code == 401:
                new_token = await refresh_token()
                if new_token:
                    token = new_token
                    # Re-construir URL con nuevo token
                    base_url = method_url.split("?")[0]
                    new_url = f"{base_url}?auth={token}"
                    return await client.post(new_url, json=payload)
            return r

        # 1. Listar bots para encontrar el ID
        list_url = f"https://{domain}/rest/imbot.bot.list?auth={token}"
        resp = await call_api(list_url)
        
        if resp.status_code != 200:
            print(f"Error al listar bots: {resp.status_code} - {resp.text}")
            return
            
        data = resp.json()
        bot_id = None
        if "result" in data:
            for bid, bdata in data["result"].items():
                if bdata.get("CODE") == bot_code:
                    bot_id = bid
                    break
        
        if not bot_id:
            print(f"No se encontró el bot con código {bot_code}")
            return
            
        print(f"Bot encontrado (ID: {bot_id}). Actualizando URL a {webhook_url}...")
        
        # 2. Actualizar el bot
        update_url = f"https://{domain}/rest/imbot.update?auth={token}"
        payload = {
            "BOT_ID": bot_id,
            "FIELDS": {
                "EVENT_HANDLER": webhook_url,
                "PROPERTIES": {
                    "NAME": bot_name,
                    "WORK_POSITION": "Asistente Virtual"
                }
            }
        }
        
        update_resp = await call_api(update_url, payload)
        update_data = update_resp.json()
        
        if update_resp.status_code == 200 and update_data.get("result"):
            print("¡Bot actualizado exitosamente!")
        else:
            print(f"Error al actualizar: {update_resp.status_code} - {update_resp.text}")

if __name__ == "__main__":
    asyncio.run(main())
