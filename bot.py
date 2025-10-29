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
import random

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

categories = {
    1: ["памятник","скульптура","монумент","статуя"],
    2: ["парк","сквер","зона","отдых","прогулка","гулять"],
    3: ["макет","объект","здание"],
    4: ["набережная","берег","река","Волга","Ока"],
    5: ["архитектура","история","постройка"],
    6: ["культура","досуг","тц","развлечения"],
    7: ["музей","выставка","галерея","пространство","искусство","художник"],
    8: ["театр","филармония"],
    9: ["города","инфраструктура"],
    10: ["монумент","искусство"],
    11: ["ресторан","кафе","еда","голоден","жрать"],
    12: ["кофе","кофейня","выпить"],
    13: ["кондитерская","пекарня","булочки","торт","пирожные"]
}

def define_categories(text):
    text = text.lower()

    found_categories = []

    for key, value in categories.items():
        for word in value:
            if word in text:
                found_categories.append(key)
                break
    
    return list(set(found_categories))

@flask_app.route('/generate_route', methods=['POST', 'OPTIONS'])
def generate_route():
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', '*')
        response.headers.add('Access-Control-Allow-Methods', '*')
        return response
    
    data = request.json

    query = data.get('query')
    hours = data.get('hours')
    minutes = data.get('minutes')
    startPoint = data.get('startPoint')

    request_categories = define_categories(query)

    ds = load_dataset()

    if ds is None:
        return jsonify({"error": "Dataset not loaded"}), 500

    list_of_places = ds[ds['category_id'].isin(request_categories)]

    #Пока что логика - брать первые 3-5 мест или если их менее 3 то дополняем случайными
    selected_places = list_of_places.head(random.randint(3,5))
    if len(selected_places) < 3:
        additional_places = ds.sample(3 - len(selected_places))
        selected_places = pd.concat([selected_places, additional_places])

    result = []
    for _, place in selected_places.iterrows():
        coords = place['coordinate'].replace("POINT (", "").replace(")", "").split()
        result.append({
            "title": place['title'],
            "address": place['address'],
            "coord": [coords[0], coords[1]],
            "description": place['description'],
            "reason": "В вашем запросе были подходящие слова!"
        })
    result.headers.add('Access-Control-Allow-Origin', '*')
    return jsonify(result)

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

    Thread(target=lambda: flask_app.run(host="0.0.0.0", port=port, debug=False)).start()

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





