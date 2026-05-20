"""
Tool: get_weather
Fetches current weather for any city using the free wttr.in JSON API.
No API key required.
Returns a short pilot-focused summary: temp, wind, visibility, humidity, sun times.
"""
import requests


def get_weather(city: str) -> str:
    """
    Fetches current weather conditions for a given city.
    """
    city = city.strip()
    if not city:
        return "ERROR: city name must not be empty."    # Prevent empty city inputs:

    url = f"https://wttr.in/{city}?format=j1"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.Timeout:
        return f"ERROR: weather request timed out for '{city}'."
    except requests.exceptions.HTTPError as e:
        return f"ERROR: could not fetch weather for '{city}' ({e})."
    except Exception as e:
        return f"ERROR: unexpected error fetching weather for '{city}': {e}."

    try:
        current = data["current_condition"][0]
        area = data["nearest_area"][0]
        astronomy = data["weather"][0]["astronomy"][0]

        city_name = area["areaName"][0]["value"]
        country = area["country"][0]["value"]
        conditions = current["weatherDesc"][0]["value"]
        temp_c = current["temp_C"]
        feels_like_c = current["FeelsLikeC"]
        wind_kmph = current["windspeedKmph"]
        wind_dir = current["winddir16Point"]
        visibility_km = current["visibility"]
        humidity = current["humidity"]
        sunrise = astronomy["sunrise"]
        sunset = astronomy["sunset"]

        # Return a concise aviation-style weather summary:
        return (
            f"Weather in {city_name}, {country}:\n"
            f"- Conditions: {conditions}\n"
            f"- Temperature: {temp_c}C (feels like {feels_like_c}C)\n"
            f"- Wind: {wind_kmph} km/h from {wind_dir}\n"
            f"- Visibility: {visibility_km} km\n"
            f"- Humidity: {humidity}%\n"
            f"- Sunrise: {sunrise}, Sunset: {sunset}"
        )

    # Handle unexpected API response formats:
    except (KeyError, IndexError) as e:
        return f"ERROR: unexpected response format from weather service: {e}."
