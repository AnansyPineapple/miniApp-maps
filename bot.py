import os
import logging
import pandas as pd
import json
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from flask import Flask, request, jsonify
from flask_cors import CORS
from threading import Thread

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

flask_app = Flask(__name__)
CORS(flask_app)

def get_bot_token():
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        load_dotenv()
        token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN was not found!")
    return token

def load_dataset():
    try:
        ds = pd.read_excel('dataset.xlsx')
        return ds
    except Exception as e:
        print(f"Ошибка загрузки датасета - {e}")
        return None

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Открыть приложение", web_app = {"url" : "https://anansypineapple.github.io/miniApp-maps/"})]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Привет, друг! Нажми кнопку ниже чтобы запустить приложение!", reply_markup = reply_markup)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Открыть приложение", web_app = {"url" : "https://anansypineapple.github.io/miniApp-maps/"})]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Чтобы начать работу необходимо запустить приложение!", reply_markup = reply_markup)

@flask_app.route('/generate_route', methods=['POST' , 'OPTIONS'])
def generate_route():
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        return response
    
    data = request.json
    print("Получен запрос:", data)

    result = {
        "places": [
            {
                "title": "Памятник Почтальону",
                "address": "ул. Большая Покровская",
                "coord": [56.331576, 44.003277],
                "description": "Бронзовый памятник почтальону в центре города.",
                "reason": "Популярное место для прогулок и фотографий."
            },
            {
                "title": "Нижегородский Кремль",
                "address": "Кремль",
                "coord": [56.3287, 44.0021],
                "description": "Историческая крепость, сердце города.",
                "reason": "Вы интересовались историческими достопримечательностями."
            }
        ]
    }
    response = jsonify(result)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

def main():
    token = get_bot_token()
    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    port = int(os.environ.get('PORT', 10000))
    #webhook_url = os.getenv('WEBHOOK_URL')
        
    #if not webhook_url:
    #    raise ValueError("WEBHOOK_URL was not set!")
        
    #    full_webhook_url = f"{webhook_url}/{token}"

    logger.info("Bot is running from Render.com")

    Thread(target=lambda: flask_app.run(host="0.0.0.0", port=port)).start()

        #app.run_webhook(
        #    listen="0.0.0.0", 
        #    port=10000, 
        #    webhook_url=full_webhook_url,
        #    url_path=token
        #   )
        
    app.run_polling()
    #logger.info("Bot is running locally")

if __name__ == "__main__":

    main()


