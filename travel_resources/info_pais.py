"""
info_pais - Información de países usando REST Countries API.
100% gratis, sin API key.
"""
import httpx

async def get_info_pais(country: str) -> dict:
    """Obtiene info general de un país: moneda, idioma, capital, etc."""
    url = f"https://restcountries.com/v3.1/name/{country}"
    params = {"fields": "name,capital,currencies,languages,timezones,region,subregion,population,flags"}

    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.get(url, params=params)
        r.raise_for_status()
        data = r.json()

    if not data:
        return {"error": f"No se encontró información para '{country}'"}

    pais = data[0]

    # Extraer moneda principal
    currencies = pais.get("currencies", {})
    moneda = ""
    for code, info in currencies.items():
        moneda = f"{info.get('name', '')} ({code}) - Símbolo: {info.get('symbol', '')}"
        break

    # Extraer idiomas
    langs = pais.get("languages", {})
    idiomas = ", ".join(langs.values()) if langs else "Desconocido"

    return {
        "nombre": pais.get("name", {}).get("common", country),
        "nombre_oficial": pais.get("name", {}).get("official", ""),
        "capital": pais.get("capital", [""])[0] if pais.get("capital") else "",
        "moneda": moneda,
        "idiomas": idiomas,
        "zona_horaria": pais.get("timezones", [""])[0],
        "region": pais.get("region", ""),
        "subregion": pais.get("subregion", ""),
        "poblacion": pais.get("population", 0),
        "bandera": pais.get("flags", {}).get("png", ""),
    }
