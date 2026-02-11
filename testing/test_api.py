import asyncio
import os
import httpx
import json
import sys
from dotenv import load_dotenv

async def test_method(method, params_json):
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
                return r.json()["access_token"]
        return None

    params = json.loads(params_json)
    url = f"https://{domain}/rest/{method}?auth={token}"
    
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.post(url, json=params)
        if resp.status_code == 401:
            token = await refresh_token()
            url = f"https://{domain}/rest/{method}?auth={token}"
            resp = await client.post(url, json=params)
        
        print(f"Status: {resp.status_code}")
        print("Response:", resp.text)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 test_api.py <method> '<params_json>'")
    else:
        asyncio.run(test_method(sys.argv[1], sys.argv[2]))
