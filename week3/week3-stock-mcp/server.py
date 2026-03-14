import httpx
from mcp.server.fastmcp import FastMCP
from mcp.server.stdio import stdio_server
mcp = FastMCP("weather-server")
from mcp.server.stdio import stdio_server
import asyncio
import sys
import traceback

# ==================================
# TOOL 1 — CURRENT WEATHER
# ==================================
@mcp.tool()
async def get_current_weather(city: str) -> dict:
    """
    Get current weather by city name
    """

    geo_url = "https://geocoding-api.open-meteo.com/v1/search"

    async with httpx.AsyncClient() as client:
        geo_res = await client.get(geo_url, params={"name": city})
        geo_data = geo_res.json()

    if "results" not in geo_data:
        return {"error": "City not found"}

    lat = geo_data["results"][0]["latitude"]
    lon = geo_data["results"][0]["longitude"]

    weather_url = "https://api.open-meteo.com/v1/forecast"

    async with httpx.AsyncClient() as client:
        weather_res = await client.get(
            weather_url,
            params={
                "latitude": lat,
                "longitude": lon,
                "current_weather": True
            }
        )

    return weather_res.json()


# ==================================
# TOOL 2 — FORECAST
# ==================================
@mcp.tool()
async def get_weather_forecast(city: str, days: int = 3) -> dict:
    """
    Get weather forecast for upcoming days
    """

    geo_url = "https://geocoding-api.open-meteo.com/v1/search"

    async with httpx.AsyncClient() as client:
        geo_res = await client.get(geo_url, params={"name": city})
        geo_data = geo_res.json()

    if "results" not in geo_data:
        return {"error": "City not found"}

    lat = geo_data["results"][0]["latitude"]
    lon = geo_data["results"][0]["longitude"]

    weather_url = "https://api.open-meteo.com/v1/forecast"

    async with httpx.AsyncClient() as client:
        weather_res = await client.get(
            weather_url,
            params={
                "latitude": lat,
                "longitude": lon,
                "daily": "temperature_2m_max,temperature_2m_min",
                "forecast_days": days,
                "timezone": "auto"
            }
        )

    return weather_res.json()

if __name__ == "__main__":
    try:
        mcp.run()
    except Exception as e:
        print("SERVER CRASHED:", e, file=sys.stderr)
        traceback.print_exc()