"""
clima_destino - Pronóstico del clima para un destino usando Open-Meteo.
100% gratis, sin API key.
"""
import httpx

async def get_clima(lat: float, lon: float, days: int = 7) -> dict:
    """Obtiene pronóstico del clima para coordenadas dadas."""
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,windspeed_10m_max,weathercode",
        "current_weather": True,
        "timezone": "auto",
        "forecast_days": min(days, 16),
    }
    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.get(url, params=params)
        r.raise_for_status()
        data = r.json()

    current = data.get("current_weather", {})
    daily = data.get("daily", {})

    forecast = []
    dates = daily.get("time", [])
    for i, date in enumerate(dates):
        forecast.append({
            "fecha": date,
            "temp_max": daily["temperature_2m_max"][i],
            "temp_min": daily["temperature_2m_min"][i],
            "lluvia_mm": daily["precipitation_sum"][i],
            "viento_max_kmh": daily["windspeed_10m_max"][i],
            "codigo_clima": daily["weathercode"][i],
        })

    return {
        "clima_actual": {
            "temperatura": current.get("temperature"),
            "viento_kmh": current.get("windspeed"),
            "codigo": current.get("weathercode"),
        },
        "pronostico_diario": forecast,
        "unidad_temp": data.get("daily_units", {}).get("temperature_2m_max", "°C"),
    }
