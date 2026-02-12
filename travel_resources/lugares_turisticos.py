"""
lugares_turisticos - Atracciones turísticas usando Overpass API (OpenStreetMap).
100% gratis, sin API key.
"""
import httpx

async def get_lugares(lat: float, lon: float, radius: int = 5000, limit: int = 10) -> dict:
    """Busca atracciones turísticas cerca de las coordenadas dadas usando Overpass (OSM)."""
    query = f"""
    [out:json][timeout:15];
    (
      node["tourism"~"attraction|museum|viewpoint|gallery|artwork"](around:{radius},{lat},{lon});
      node["historic"](around:{radius},{lat},{lon});
      node["leisure"~"park|garden"](around:{radius},{lat},{lon});
    );
    out body {limit};
    """

    url = "https://overpass-api.de/api/interpreter"

    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.post(url, data={"data": query})
        r.raise_for_status()
        data = r.json()

    elements = data.get("elements", [])

    if not elements:
        return {"lugares": [], "mensaje": "No se encontraron atracciones cercanas."}

    resultado = []
    for el in elements:
        tags = el.get("tags", {})
        nombre = tags.get("name", tags.get("name:es", "Sin nombre"))
        tipo = tags.get("tourism") or tags.get("historic") or tags.get("leisure") or ""
        resultado.append({
            "nombre": nombre,
            "tipo": tipo,
            "lat": el.get("lat"),
            "lon": el.get("lon"),
        })

    return {"lugares": resultado}
