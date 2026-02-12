"""
zona_horaria - Hora local de un destino usando WorldTimeAPI.
100% gratis, sin API key.
"""
import httpx

async def get_zona_horaria(timezone: str) -> dict:
    """Obtiene la hora local de una zona horaria (ej: 'America/Bogota')."""
    url = f"http://worldtimeapi.org/api/timezone/{timezone}"

    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.get(url)
        r.raise_for_status()
        data = r.json()

    return {
        "zona_horaria": data.get("timezone", timezone),
        "hora_local": data.get("datetime", ""),
        "utc_offset": data.get("utc_offset", ""),
        "abreviatura": data.get("abbreviation", ""),
        "dia_semana": data.get("day_of_week", ""),
    }


async def listar_zonas() -> list:
    """Lista todas las zonas horarias disponibles."""
    url = "http://worldtimeapi.org/api/timezone"
    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.get(url)
        r.raise_for_status()
        return r.json()
