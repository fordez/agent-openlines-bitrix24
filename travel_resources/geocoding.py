"""
geocoding - Convierte nombre de ciudad a coordenadas usando Nominatim (OpenStreetMap).
100% gratis, sin API key.
"""
import httpx

async def geocode(city: str) -> dict:
    """Convierte nombre de ciudad a coordenadas lat/lon."""
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": city,
        "format": "json",
        "limit": 1,
        "accept-language": "es",
    }
    headers = {"User-Agent": "BotViajes/1.0"}
    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.get(url, params=params, headers=headers)
        r.raise_for_status()
        results = r.json()

    if not results:
        return {"error": f"No se encontraron resultados para '{city}'"}

    place = results[0]
    return {
        "nombre": place.get("display_name", city),
        "lat": float(place["lat"]),
        "lon": float(place["lon"]),
        "tipo": place.get("type", ""),
    }
