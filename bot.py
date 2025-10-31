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
from sentence_transformers import SentenceTransformer, util
import requests
import torch
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

flask_app = Flask(__name__)
CORS(flask_app)

HF_API_TOKEN = "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"
HF_API_URL = "https://api-inference.huggingface.co/models/sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}

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
        [InlineKeyboardButton("Открыть приложение", web_app={"url": "https://anansypineapple.github.io/miniApp-maps/"})]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Привет, друг! Нажми кнопку ниже чтобы запустить приложение!",
                                    reply_markup=reply_markup)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Открыть приложение", web_app={"url": "https://anansypineapple.github.io/miniApp-maps/"})]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Чтобы начать работу необходимо запустить приложение!", reply_markup=reply_markup)

#Чтобы в консоль не было информировании о запуске модели
#logging.getLogger("sentence_transformers").setLevel(logging.WARNING)

#Сама модель для работы с запросом
#model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
#model = model.half()

def get_embeddings(texts):
    if isinstance(texts, str):
        texts = [texts]
    
    response = requests.post(
        HF_API_URL, 
        headers=headers, 
        json={"inputs": texts, "wait_for_model": True}
    )
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Ошибка HF API: {response.status_code} - {response.text}")
        return None

def load_category_embeddings():
    category_names = [
        "Памятники и скульптуры",
        "Парки, скверы и зоны отдыха",
        "Макеты архитектурных объектов",
        "Набережные",
        "Архитектура и исторические здания",
        "Культурно-досуговые центры и библиотеки",
        "Музеи и выставочные пространства",
        "Театры и филармонии",
        "Инфраструктура",
        "Монументально-декоративное искусство",
        "Рестораны и кафе",
        "Кофейни",
        "Кондитерские и пекарни",
        "Торговые центры",
        "Места для развлечения"
    ]
    
    embeddings = get_embeddings(category_names)
    if embeddings:
        return torch.tensor(embeddings)

category_embeddings = load_category_embeddings()

#Перевод для дальнейшего сравнения
#category_embeddings = model.encode(category_names, convert_to_tensor=True, show_progress_bar=False)

#Перегрузка функции, которая возвращает топ категории мест
def define_categories(text, similarity_threshold=0.5, min_categories=3, max_categories=5):
    """
    Определяет топ категорий для запроса пользователя с использованием sentence-transformers.

    Параметры:
        text (str) - текст запроса пользователя
        similarity_threshold (float) - минимальное значение косинусного сходства для включения категории
        min_categories (int) - минимальное количество категорий в топе
        max_categories (int) - максимальное количество категорий в топе

    Возвращает:
        list of tuples: [(category_id, score), ...] — топ категорий с их схожестью
    """

#Кодируем запрос в вектор с помощью модели sentence-transformers.
    query_emb = get_embeddings(text)
    query_emb = torch.tensor(query_emb)
#Считаем косинусное сходство запроса с векторами категорий.
    similarities = util.cos_sim(query_emb, category_embeddings)[0]

#Сортируем категории по схожести.
    sorted_indices = torch.argsort(similarities, descending=True).tolist()
    sorted_scores = similarities[sorted_indices].tolist()

    found=[]

#Добавляем в результат только те, у которых сходство ≥ similarity_threshold.
    for idx, score in zip(sorted_indices, sorted_scores):
        if score >= similarity_threshold:
            found.append((idx+1, score))
        if len(found) >= max_categories:
            break
#Если найдено меньше min_categories, добавляем следующие по схожести, чтобы гарантировать минимум.
    if len(found) < min_categories:
        for idx, score in zip(sorted_indices, sorted_scores):
            if (idx + 1, score) not in found:
                found.append((idx + 1, score))
            if len(found) >= min_categories:
                break

#Возвращаем список кортежей (category_id, score).
    return found[:max_categories]

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

    request_categories = define_categories(query)

    ds = load_dataset()

    list_of_places = ds[ds['category_id'].isin(request_categories)]

    # Пока что логика - брать первые 3-5 мест или если их менее 3 то дополняем случайными
    selected_places = list_of_places.head(min(5, len(list_of_places)))
    if len(selected_places) < 3:
        additional_places = ds.sample(3 - len(selected_places))
        selected_places = pd.concat([selected_places, additional_places])

    result = {
        "startPoint": startPoint,
        "places": []
    }

    for _, place in selected_places.iterrows():
        coords = place['coordinate'].replace("POINT (", "").replace(")", "").split()
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

#Тест функции по схожести запроса и категорий
def test1():
    test_queries = [
        "Хочу прогуляться по парку и посмотреть памятники",
        "Ищу хороший ресторан с кофе и десертами",
        "Посетить музей и выставку искусства",
        "Прогуляться по набережной Волги",
        "Что-то историческое и архитектурное"
    ]
    for query in test_queries:
        categories_found = define_categories(query)
        print(f"Запрос: {query}")
        for cat_id, score in categories_found:
            label = category_names[cat_id - 1]
            if score is not None:
                print(f"  Категория {cat_id}: {label}, схожесть = {score:.3f}")
            else:
                print(f"  Категория {cat_id}: {label} (fallback)")
        print("-" * 40)

#Тест на составление таблицы кандидатов
def test2():
    ds = load_dataset()
    query="Хочу прогуляться по парку и посмотреть памятники"
    candidates = get_candidate_places(query, ds)
    print("Все кандидаты для маршрута:")
    print(candidates[['title', 'category_id', 'score']].sort_values(by='score', ascending=False))


def main():
    token = get_bot_token()
    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    port = int(os.environ.get('PORT', 10000))
    # webhook_url = os.getenv('WEBHOOK_URL')

    # if not webhook_url:
    #    raise ValueError("WEBHOOK_URL was not set!")

    #    full_webhook_url = f"{webhook_url}/{token}"

    logger.info("Bot is running from Render.com")

    Thread(target=lambda: flask_app.run(host="0.0.0.0", port=port, debug=False)).start()

    # app.run_webhook(
    #    listen="0.0.0.0",
    #    port=10000,
    #    webhook_url=full_webhook_url,
    #    url_path=token
    #   )

    app.run_polling()
    # logger.info("Bot is running locally")


if __name__ == "__main__":
    test1()
#    test2()
#    main()

