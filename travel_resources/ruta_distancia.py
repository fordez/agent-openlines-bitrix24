"""
ruta_distancia - Calcula rutas y distancias entre dos puntos usando OSRM.
100% gratis, sin API key.
"""
import httpx

async def get_ruta(origin_lat: float, origin_lon: float, dest_lat: float, dest_lon: float) -> dict:
    """Calcula distancia y tiempo de viaje por carretera."""
    url = f"http://router.project-osrm.org/route/v1/driving/{origin_lon},{origin_lat};{dest_lon},{dest_lat}"
    params = {"overview": "false", "alternatives": "false"}

    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.get(url, params=params)
        r.raise_for_status()
        data = r.json()

    if data.get("code") != "Ok" or not data.get("routes"):
        return {"error": "No se pudo calcular la ruta"}

    route = data["routes"][0]
    dist_km = round(route["distance"] / 1000, 1)
    duration_min = round(route["duration"] / 60)
    hours = duration_min // 60
    mins = duration_min % 60

    return {
        "distancia_km": dist_km,
        "duracion_minutos": duration_min,
        "duracion_texto": f"{hours}h {mins}min" if hours else f"{mins} min",
    }
