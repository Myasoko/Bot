import logging
import sys

from telegram.error import InvalidToken
from telegram.ext import Application, CommandHandler, MessageHandler, filters

from config import TOKEN
from handlers import start_command, handle_message, error_handler
from weather import close_session

LOG_FORMAT = "%(asctime)s | %(name)s | %(levelname)s | %(message)s"


class RedactingFormatter(logging.Formatter):
    """Hide the bot token in every log line, including tracebacks."""

    def format(self, record: logging.LogRecord) -> str:
        return super().format(record).replace(TOKEN, "<TOKEN>")


logging.basicConfig(format=LOG_FORMAT, level=logging.INFO)
for handler in logging.getLogger().handlers:
    handler.setFormatter(RedactingFormatter(LOG_FORMAT))

# httpx logs full request URLs at INFO level, and they contain the bot token
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


async def on_shutdown(app: Application) -> None:
    """Close the shared HTTP session when the bot stops."""
    await close_session()


def main() -> None:
    logger.info("Starting bot")
    app = (
        Application.builder()
        .token(TOKEN)
        .post_shutdown(on_shutdown)
        .build()
    )

    # COMMANDS
    app.add_handler(CommandHandler("start", start_command))

    # MESSAGES
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # ERRORS
    app.add_error_handler(error_handler)

    # Polling
    logger.info("Polling")
    try:
        app.run_polling()
    except InvalidToken:
        # Exit with a short message instead of a traceback that contains the token
        logger.error("Telegram rejected the token. Check TELEGRAM_TOKEN in .env")
        sys.exit(1)


if __name__ == "__main__":
    main()