import os
from typing import Final

from dotenv import load_dotenv

load_dotenv()


def _require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(
            f"Environment variable {name} is not set. "
            "Create a .env file based on .env.example"
        )
    return value


BOT_USERNAME: Final = "@wearecheck_bot"
TOKEN: Final = _require_env("TELEGRAM_TOKEN")
API_KEY: Final = _require_env("OPENWEATHER_API_KEY")