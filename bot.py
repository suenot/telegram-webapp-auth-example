import telebot
import os
import logging
from dotenv import load_dotenv
from telebot import types

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
WEBAPP_URL = os.getenv('WEBAPP_URL')

if not TELEGRAM_BOT_TOKEN:
    logger.error("Error: TELEGRAM_BOT_TOKEN environment variable not set.")
    exit()

if not WEBAPP_URL:
    logger.error("Error: WEBAPP_URL environment variable not set.")
    exit()

# Initialize the bot
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

logger.info("Bot started...")

@bot.message_handler(commands=['start', 'login'])
def send_welcome(message):
    logger.info(f"Received /start command from chat_id: {message.chat.id}")
    markup = types.InlineKeyboardMarkup()
    # Create the WebApp button
    web_app_button = types.WebAppInfo(WEBAPP_URL)
    button = types.InlineKeyboardButton(text="Open Web App 🔐", web_app=web_app_button)
    markup.add(button)

    bot.send_message(
        message.chat.id,
        "Hello! Click the button below to securely log in via our Web App.",
        reply_markup=markup
    )
    logger.info(f"Sent WebApp button to chat_id: {message.chat.id}")

if __name__ == '__main__':
    try:
        bot.polling(non_stop=True)
    except Exception as e:
        logger.error(f"Bot polling failed: {e}") 