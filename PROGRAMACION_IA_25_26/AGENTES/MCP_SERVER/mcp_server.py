# MCP Server
# Instalación de la librería FastMCP
# !pip install fastmcp
# !pip install httpx

from fastmcp import FastMCP
import httpx

mcp = FastMCP("mi-servidor-mcp")

@mcp.tool
def obtener_tiempo(ciudad: str) -> dict:
    """Obtiene el clima actual real para cualquier ciudad."""
    
    # Paso 1: Geocodificación — convertir nombre de ciudad a coordenadas
    geo_url = "https://geocoding-api.open-meteo.com/v1/search"
    geo_params = {"name": ciudad, "count": 1, "language": "es", "format": "json"}
    
    geo_response = httpx.get(geo_url, params=geo_params)
    geo_data = geo_response.json()
    
    if not geo_data.get("results"):
        return {"ciudad": ciudad, "error": "Ciudad no encontrada"}
    
    lugar = geo_data["results"][0]
    lat = lugar["latitude"]
    lon = lugar["longitude"]
    nombre_oficial = lugar["name"]
    pais = lugar.get("country", "")
    
    # Paso 2: Obtener el clima con las coordenadas
    clima_url = "https://api.open-meteo.com/v1/forecast"
    clima_params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code",
        "timezone": "auto"
    }
    
    clima_response = httpx.get(clima_url, params=clima_params)
    clima_data = clima_response.json()
    current = clima_data["current"]
    
    # Paso 3: Traducir el código de clima a descripción
    weather_codes = {
        0: "despejado", 1: "casi despejado", 2: "parcialmente nublado", 3: "nublado",
        45: "niebla", 48: "niebla con escarcha",
        51: "llovizna ligera", 53: "llovizna", 55: "llovizna intensa",
        61: "lluvia ligera", 63: "lluvia", 65: "lluvia intensa",
        71: "nieve ligera", 73: "nieve", 75: "nieve intensa",
        80: "chubascos ligeros", 81: "chubascos", 82: "chubascos intensos",
        95: "tormenta", 96: "tormenta con granizo", 99: "tormenta con granizo intenso"
    }
    codigo = current["weather_code"]
    condicion = weather_codes.get(codigo, f"código {codigo}")
    
    return {
        "ciudad": nombre_oficial,
        "pais": pais,
        "temperatura": f"{current['temperature_2m']}°C",
        "humedad": f"{current['relative_humidity_2m']}%",
        "viento": f"{current['wind_speed_10m']} km/h",
        "condicion": condicion
    }

@mcp.tool
def calcular(expresion: str) -> dict:
    """Evalúa de forma segura una expresión matemática."""
    try:
        # Solo se permiten operaciones matemáticas básicas
        caracteres_permitidos = set("0123456789+-*/.() ")
        if not all(c in caracteres_permitidos for c in expresion):
            return {"error": "La expresión contiene caracteres no permitidos"}
        
        resultado = eval(expresion)  # Seguro porque validamos la entrada
        return {"expresion": expresion, "resultado": resultado}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    mcp.run(transport="stdio")
