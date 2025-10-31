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
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

flask_app = Flask(__name__)
CORS(flask_app)

AI_MODEL_URL = "https://miniapp-maps-aimodel.onrender.com"

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

#Перегрузка функции, которая возвращает топ категории мест
@flask_app.route('/define_categories', methods=['POST'])
def define_categories(text, similarity_threshold=0.5, min_categories=3, max_categories=5):
    response = requests.post(
        f"{AI_MODEL_URL}/define_categories", 
        json = {
            'text': text,
            'similarity_threshold': similarity_threshold,
            'min_categories': min_categories,
            'max_categories': max_categories
        }, 
        timeout = 30
    )
    return response.json()['categories']

def get_candidate_places(query, ds):
    """
    Формирует массив всех мест, соответствующих топ-категориям запроса.

    Параметры:
        query (str) - текст запроса пользователя
        ds (pd.DataFrame) - датасет с местами, должен содержать колонки:
            'title', 'address', 'coordinate', 'description', 'category_id'

    Возвращает:
        pd.DataFrame - все места из топ-категорий с добавленным столбцом 'score'
    """
    #Вызываем define_categories(query) для определения топ категорий.
    top_categories_with_score = define_categories(query)

    top_categories_ids=[cid for cid, score in top_categories_with_score]

    #Берём все места из датасета, у которых category_id входит в топ.
    candidate_places=ds[ds['category_id'].isin(top_categories_ids)].copy()

    #Добавляем столбец score, соответствующий релевантности категории запросу.
    score_dict = {cid: score for cid, score in top_categories_with_score}
    candidate_places['score']=candidate_places['category_id'].apply(lambda x: score_dict.get(x, 0))

    #Возвращаем DataFrame с кандидатами для маршрута.
    return candidate_places

@flask_app.route('/generate_route', methods=['POST', 'OPTIONS'])
def generate_route():
    logger.info("generate_route called")
    
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

    request_categories = [cid for cid, score in define_categories(query, ds)]

    ds = load_dataset()

    list_of_places = ds[ds['category_id'].isin(request_categories)]

    #Пока что логика - брать первые 3-5 мест или если их менее 3 то дополняем случайными 
    selected_places = list_of_places.head(min(5, len(list_of_places)))
    if len(selected_places) < 3:
        additional_places = ds.sample(3 - len(selected_places))
        selected_places = pd.concat([selected_places, additional_places])

    result = {
        "startPoint": startPoint,
        "places": [],
        "time": f"{hours}.{minutes}"
    }

    for _, place in selected_places.iterrows():
        coords = place['coordinate'].replace("POINT(", "").replace(")", "").split()
        result["places"].append({
            "title": place['title'],
            "address": place['address'],
            "coord": [coords[0], coords[1]],
            "description": place['description'],
            "reason": "В вашем запросе были подходящие слова!"
        })
    
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