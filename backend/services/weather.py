"""OutfitCheck AI - Weather Service using Open-Meteo API (Free, no API key needed)"""
import httpx


async def get_weather(city: str = "Bucharest") -> dict:
    """
    Get current weather data for a city using Open-Meteo.
    Returns temperature, description, icon URL, and clothing recommendations.
    """
    try:
        async with httpx.AsyncClient() as client:
            # 1. Geocoding API to get latitude and longitude for the city
            geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=en&format=json"
            geo_response = await client.get(geo_url)
            geo_data = geo_response.json()

            if not geo_data.get("results"):
                return _default_weather(city)

            lat = geo_data["results"][0]["latitude"]
            lon = geo_data["results"][0]["longitude"]
            city_name = geo_data["results"][0]["name"]

            # 2. Weather Forecast API using the coordinates
            weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,apparent_temperature,weather_code"
            weather_response = await client.get(weather_url)
            w_data = weather_response.json()

            current = w_data["current"]
            temp = current["temperature_2m"]
            feels_like = current["apparent_temperature"]
            weather_code = current["weather_code"]

            # Map the WMO weather code to a description and icon URL
            description, icon_code = _map_wmo_code(weather_code)
            icon_url = f"https://openweathermap.org/img/wn/{icon_code}@2x.png"

            return {
                "city": city_name,
                "temperature": round(temp),
                "feels_like": round(feels_like),
                "description": description,
                "icon": icon_url,
                "clothing_hint": _get_clothing_hint(temp),
                "season_hint": _get_season_hint(temp)
            }
    except Exception as e:
        print(f"Weather API error: {e}")
        return _default_weather(city)


def _map_wmo_code(code: int) -> tuple[str, str]:
    """Map Open-Meteo WMO weather codes to text description and OpenWeatherMap icon codes for the UI."""
    # Mapping based on WMO standard
    if code == 0:
        return "Clear sky", "01d"
    elif code == 1:
        return "Mainly clear", "02d"
    elif code == 2:
        return "Partly cloudy", "03d"
    elif code == 3:
        return "Overcast", "04d"
    elif code in [45, 48]:
        return "Fog", "50d"
    elif code in [51, 53, 55, 56, 57]:
        return "Drizzle", "09d"
    elif code in [61, 63, 65, 66, 67]:
        return "Rain", "10d"
    elif code in [71, 73, 75, 77]:
        return "Snow", "13d"
    elif code in [80, 81, 82]:
        return "Rain showers", "09d"
    elif code in [85, 86]:
        return "Snow showers", "13d"
    elif code in [95, 96, 99]:
        return "Thunderstorm", "11d"
    else:
        return "Unknown weather", "02d"


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
        "icon": "https://openweathermap.org/img/wn/02d@2x.png",
        "clothing_hint": "T-shirt, light pants or skirt, comfortable shoes",
        "season_hint": "spring"
    }
