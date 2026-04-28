"""OutfitCheck AI - Weather Service using OpenWeatherMap API"""
import httpx
from backend.config import WEATHER_API_KEY


async def get_weather(city: str = "Bucharest") -> dict:
    """
    Get current weather data for a city.
    Returns temperature, description, and clothing recommendations.
    """
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": city,
            "appid": WEATHER_API_KEY,
            "units": "metric",
            "lang": "en"
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)

            if response.status_code != 200:
                # Return default weather if API fails
                return _default_weather(city)

            data = response.json()

            temp = data["main"]["temp"]
            feels_like = data["main"]["feels_like"]
            description = data["weather"][0]["description"]
            icon = data["weather"][0]["icon"]

            return {
                "city": city,
                "temperature": round(temp),
                "feels_like": round(feels_like),
                "description": description,
                "icon": f"https://openweathermap.org/img/wn/{icon}@2x.png",
                "clothing_hint": _get_clothing_hint(temp),
                "season_hint": _get_season_hint(temp)
            }
    except Exception:
        return _default_weather(city)


def _get_clothing_hint(temp: float) -> str:
    """Get clothing recommendation based on temperature."""
    if temp < 0:
        return "Heavy winter coat, layers, scarf, gloves, and warm boots"
    elif temp < 10:
        return "Warm jacket, layers, closed shoes"
    elif temp < 18:
        return "Light jacket or sweater, jeans, comfortable shoes"
    elif temp < 25:
        return "T-shirt, light pants or skirt, comfortable shoes"
    elif temp < 30:
        return "Light, breathable clothing, sandals or sneakers"
    else:
        return "Very light clothing, shorts, sandals, sun protection"


def _get_season_hint(temp: float) -> str:
    """Map temperature to season-like category."""
    if temp < 5:
        return "winter"
    elif temp < 15:
        return "autumn"
    elif temp < 25:
        return "spring"
    else:
        return "summer"


def _default_weather(city: str) -> dict:
    """Default weather when API is unavailable."""
    return {
        "city": city,
        "temperature": 20,
        "feels_like": 20,
        "description": "moderate weather",
        "icon": "",
        "clothing_hint": "T-shirt, light pants or skirt, comfortable shoes",
        "season_hint": "spring"
    }
