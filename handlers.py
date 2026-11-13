import logging
import re

from telegram import Update
from telegram.ext import ContextTypes

from config import BOT_USERNAME
from weather import get_weather

logger = logging.getLogger(__name__)

GROUP_CHAT_TYPES = ("group", "supergroup")


# COMMANDS
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Hello, I'm a Weather Bot. I can help you check the weather! 🌦\n"
        "To check the weather, please type the name of your city."
    )


# RESPONSES
async def handle_response(text: str) -> str:
    city = text.strip()
    if not city:
        return "🌤️ Please enter a city name."
    return await get_weather(city)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.message
    # update.message can be None (e.g. for edited messages)
    if message is None or not message.text:
        return

    chat_type = message.chat.type
    text = message.text

    # Log metadata only, not the message text (personal data)
    logger.info("Message from chat %s (%s)", message.chat.id, chat_type)

    if chat_type in GROUP_CHAT_TYPES:
        # In groups, reply only when the bot is mentioned (case-insensitive)
        if BOT_USERNAME.lower() not in text.lower():
            return
        text = re.sub(re.escape(BOT_USERNAME), "", text, flags=re.IGNORECASE)

    response = await handle_response(text)
    await message.reply_text(response)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error("Exception while handling an update:", exc_info=context.error)