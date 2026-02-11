import asyncio
import os
import httpx
import json
from dotenv import load_dotenv

async def list_methods():
    load_dotenv()
    domain = os.getenv("BITRIX_DOMAIN").strip("'\"")
    token = os.getenv("ACCESS_TOKEN").strip("'\"")
    
    async def refresh_token():
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
        async with httpx.AsyncClient() as client:
            r = await client.post(token_url, params=params)
            if r.status_code == 200:
                data = r.json()
                return data["access_token"]
        return None

    async def call_with_retry(url):
        nonlocal token
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(url)
            if resp.status_code == 401:
                new_token = await refresh_token()
                if new_token:
                    token = new_token
                    new_url = url.split("?")[0] + f"?auth={token}"
                    return await client.post(new_url)
            return resp

    url = f"https://{domain}/rest/methods?auth={token}"
    print(f"Listando métodos im en {domain}...")
    try:
        resp = await call_with_retry(url)
        data = resp.json()
        if "result" in data:
            im_methods = [m for m in data["result"] if m.startswith("im.")]
            print(f"Métodos im encontrados ({len(im_methods)}):")
            for m in sorted(im_methods):
                print(f" - {m}")
        else:
            print("Error:", data)
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    asyncio.run(list_methods())
