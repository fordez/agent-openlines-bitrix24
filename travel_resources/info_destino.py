"""
info_destino - Información turística de un destino usando Wikipedia API.
100% gratis, sin API key.
"""
import httpx

async def get_info_destino(city: str, lang: str = "es") -> dict:
    """Obtiene un resumen de Wikipedia sobre un destino turístico."""
    url = f"https://{lang}.wikipedia.org/api/rest_v1/page/summary/{city}"

    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.get(url)
        if r.status_code == 404:
            # Intentar búsqueda
            search_url = f"https://{lang}.wikipedia.org/w/api.php"
            search_params = {
                "action": "query",
                "list": "search",
                "srsearch": city,
                "srlimit": 1,
                "format": "json",
            }
            r2 = await client.get(search_url, params=search_params)
            r2.raise_for_status()
            results = r2.json().get("query", {}).get("search", [])
            if not results:
                return {"error": f"No se encontró información sobre '{city}' en Wikipedia."}
            # Reintentar con el título encontrado
            title = results[0]["title"]
            r = await client.get(f"https://{lang}.wikipedia.org/api/rest_v1/page/summary/{title}")

        r.raise_for_status()
        data = r.json()

    return {
        "titulo": data.get("title", city),
        "descripcion": data.get("description", ""),
        "resumen": data.get("extract", ""),
        "imagen": data.get("thumbnail", {}).get("source", ""),
        "url": data.get("content_urls", {}).get("desktop", {}).get("page", ""),
    }
