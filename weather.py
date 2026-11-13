import logging

import aiohttp

from config import API_KEY

logger = logging.getLogger(__name__)

API_URL = "https://api.openweathermap.org/data/2.5/weather"
TIMEOUT = aiohttp.ClientTimeout(total=10)

_session: aiohttp.ClientSession | None = None


def _get_session() -> aiohttp.ClientSession:
    """Return a single shared session (created on the first request)."""
    global _session
    if _session is None or _session.closed:
        _session = aiohttp.ClientSession(timeout=TIMEOUT)
    return _session


async def close_session() -> None:
    """Close the shared session when the bot shuts down."""
    if _session is not None and not _session.closed:
        await _session.close()


async def get_weather(city: str) -> str:
    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric",
        "lang": "en",
    }

    try:
        async with _get_session().get(API_URL, params=params) as response:
            status = response.status
            data = await response.json(content_type=None)
    except (aiohttp.ClientError, TimeoutError):
        logger.exception("Network error while requesting weather")
        return "⚠️ Weather service is unavailable. Please try again later."
    except ValueError:
        logger.exception("Invalid JSON from weather API")
        return "⚠️ Error retrieving the weather."

    if status == 404:
        return "City not found ❌"
    if status == 429:
        return "⏳ Too many requests. Please try again in a minute."
    if status != 200:
        # 401 (invalid key) and others: the user doesn't need details, the logs do
        logger.error("Weather API returned status %s: %s", status, data)
        return "⚠️ Error retrieving the weather."

    try:
        name = data["name"]
        temp = data["main"]["temp"]
        feels_like = data["main"]["feels_like"]
        desc = data["weather"][0]["description"]
    except (KeyError, IndexError, TypeError):
        logger.exception("Unexpected response format: %s", data)
        return "⚠️ Error retrieving the weather."

    return (
        f"📍 {name}\n\n"
        f"🌡️ Temp: {temp:.1f}°C\n"
        f"🤔 Feels like: {feels_like:.1f}°C\n"
        f"☁️ {desc.capitalize()}"
    )