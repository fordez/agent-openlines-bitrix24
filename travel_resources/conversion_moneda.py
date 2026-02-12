"""
conversion_moneda - Conversión de monedas usando ExchangeRate API.
100% gratis, sin API key.
"""
import httpx

async def convertir_moneda(from_currency: str, to_currency: str, amount: float = 1.0) -> dict:
    """Convierte una cantidad de una moneda a otra en tiempo real."""
    url = f"https://api.exchangerate.host/convert"
    params = {
        "from": from_currency.upper(),
        "to": to_currency.upper(),
        "amount": amount,
    }

    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.get(url, params=params)
        r.raise_for_status()
        data = r.json()

    if not data.get("success", True):
        # Fallback: usar endpoint alternativo
        url2 = f"https://api.exchangerate.host/latest?base={from_currency.upper()}&symbols={to_currency.upper()}"
        async with httpx.AsyncClient(timeout=15) as client:
            r = await client.get(url2)
            r.raise_for_status()
            data2 = r.json()
            rate = data2.get("rates", {}).get(to_currency.upper(), 0)
            return {
                "de": from_currency.upper(),
                "a": to_currency.upper(),
                "cantidad_original": amount,
                "tasa": rate,
                "resultado": round(amount * rate, 2),
            }

    return {
        "de": from_currency.upper(),
        "a": to_currency.upper(),
        "cantidad_original": amount,
        "tasa": data.get("info", {}).get("rate", data.get("result", 0) / amount if amount else 0),
        "resultado": round(data.get("result", 0), 2),
    }
