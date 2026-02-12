"""
MCP Travel Intelligence Server — Segundo servidor MCP.
Solo expone RESOURCES y PROMPTS para planificación de viajes.
Usa APIs 100% gratuitas.
"""
from mcp.server.fastmcp import FastMCP
import json
import traceback

mcp = FastMCP("travel_intel")

# ─────────────────────────────────────────────
# RESOURCES
# ─────────────────────────────────────────────

@mcp.resource("travel://clima/{city}")
async def resource_clima(city: str) -> str:
    """Pronóstico del clima para una ciudad (próximos 7 días).
    Incluye temperatura, lluvia, viento. Usa Open-Meteo (gratis).
    """
    try:
        from travel_resources.geocoding import geocode
        from travel_resources.clima_destino import get_clima

        geo = await geocode(city)
        if "error" in geo:
            return json.dumps(geo, ensure_ascii=False)

        clima = await get_clima(geo["lat"], geo["lon"])
        clima["ciudad"] = geo["nombre"]
        return json.dumps(clima, ensure_ascii=False, indent=2)
    except Exception as e:
        traceback.print_exc()
        return json.dumps({"error": str(e)}, ensure_ascii=False)


@mcp.resource("travel://geocoding/{city}")
async def resource_geocoding(city: str) -> str:
    """Convierte nombre de ciudad a coordenadas (lat/lon).
    Usa Nominatim / OpenStreetMap (gratis).
    """
    try:
        from travel_resources.geocoding import geocode
        result = await geocode(city)
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


@mcp.resource("travel://ruta/{origin}/{destination}")
async def resource_ruta(origin: str, destination: str) -> str:
    """Calcula distancia y tiempo de viaje por carretera entre dos ciudades.
    Usa OSRM (gratis).
    """
    try:
        from travel_resources.geocoding import geocode
        from travel_resources.ruta_distancia import get_ruta

        geo_origin = await geocode(origin)
        geo_dest = await geocode(destination)

        if "error" in geo_origin:
            return json.dumps(geo_origin, ensure_ascii=False)
        if "error" in geo_dest:
            return json.dumps(geo_dest, ensure_ascii=False)

        ruta = await get_ruta(geo_origin["lat"], geo_origin["lon"], geo_dest["lat"], geo_dest["lon"])
        ruta["origen"] = geo_origin["nombre"]
        ruta["destino"] = geo_dest["nombre"]
        return json.dumps(ruta, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


@mcp.resource("travel://lugares/{city}")
async def resource_lugares(city: str) -> str:
    """Top atracciones turísticas cerca de una ciudad.
    Usa OpenTripMap (gratis con API key).
    """
    try:
        from travel_resources.geocoding import geocode
        from travel_resources.lugares_turisticos import get_lugares

        geo = await geocode(city)
        if "error" in geo:
            return json.dumps(geo, ensure_ascii=False)

        lugares = await get_lugares(geo["lat"], geo["lon"])
        lugares["ciudad"] = geo["nombre"]
        return json.dumps(lugares, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


@mcp.resource("travel://pais/{country}")
async def resource_pais(country: str) -> str:
    """Información general de un país: moneda, idioma, capital, zona horaria, población.
    Usa REST Countries (gratis).
    """
    try:
        from travel_resources.info_pais import get_info_pais
        result = await get_info_pais(country)
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


@mcp.resource("travel://moneda/{from_currency}/{to_currency}/{amount}")
async def resource_moneda(from_currency: str, to_currency: str, amount: str) -> str:
    """Convierte una cantidad de una moneda a otra en tiempo real.
    Usa ExchangeRate.host (gratis).
    """
    try:
        from travel_resources.conversion_moneda import convertir_moneda
        result = await convertir_moneda(from_currency, to_currency, float(amount))
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


@mcp.resource("travel://horario/{timezone}")
async def resource_horario(timezone: str) -> str:
    """Hora local actual de una zona horaria (ej: America/Bogota).
    Usa WorldTimeAPI (gratis).
    """
    try:
        from travel_resources.zona_horaria import get_zona_horaria
        result = await get_zona_horaria(timezone)
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


@mcp.resource("travel://destino/{city}")
async def resource_destino(city: str) -> str:
    """Resumen turístico de un destino desde Wikipedia (historia, cultura, datos clave).
    Gratis, sin API key.
    """
    try:
        from travel_resources.info_destino import get_info_destino
        result = await get_info_destino(city)
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


# ─────────────────────────────────────────────
# PROMPTS
# ─────────────────────────────────────────────

@mcp.prompt()
def travel_planning_advisor() -> str:
    """Guía al agente para interpretar datos de viaje y responder de forma breve, persuasiva y cálida."""
    return """Eres un asesor de viajes experto. Cuando el usuario pregunte sobre un destino:

ESTILO DE RESPUESTA:
- Sé BREVE y CONCISO: máximo 3-4 líneas por punto.
- Sé PERSUASIVO: haz que el cliente quiera viajar YA.
- Sé CÁLIDO: usa un tono amigable, cercano, como un amigo que sabe de viajes.
- NO inventes datos. SIEMPRE consulta los recursos antes de responder.

FLUJO RECOMENDADO:
1. Cuando el cliente mencione un destino, consulta travel://destino/{ciudad} para enriquecer tu respuesta con datos reales.
2. Consulta travel://clima/{ciudad} para recomendar la mejor época o preparar al cliente para el clima.
3. Usa travel://pais/{pais} para dar contexto rápido: moneda, idioma, zona horaria.
4. Si el cliente pregunta por costos, usa travel://moneda/{de}/{a}/{cantidad} para conversión real.
5. Si planifica itinerario, usa travel://ruta/{origen}/{destino} para distancias reales.
6. Sugiere lugares con travel://lugares/{ciudad}.

FORMATO DE RESPUESTA (cuando tengas datos):
Presenta la info como una "tarjeta rápida":
  [Ciudad/Destino]
  Clima: [temp actual], [lluvia esperada]
  Moneda: [moneda local] (1 USD = X)
  Idioma: [idioma]
  Imperdible: [2-3 atracciones top]
  Tip: [un consejo práctico]

REGLA DE ORO: Nunca des un muro de texto. El cliente quiere respuestas rápidas y accionables."""


@mcp.prompt()
def destination_comparison() -> str:
    """Guía al agente para comparar dos destinos de forma objetiva."""
    return """Cuando el cliente dude entre dos destinos, compáralos lado a lado:

1. Consulta travel://destino, travel://clima y travel://pais para ambos.
2. Presenta una comparación rápida:

  [Destino A] vs [Destino B]
  Clima: A tiene X°C / B tiene Y°C
  Costo: A usa [moneda] / B usa [moneda]
  Atractivo: A destaca por... / B destaca por...
  Veredicto: "Si buscas [X], ve a A. Si prefieres [Y], ve a B."

Sé objetivo pero siempre cierra con una recomendación clara."""


# ─────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────

if __name__ == "__main__":
    mcp.run(transport="stdio")
