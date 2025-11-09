import os
import logging
import pandas as pd
import json
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
from threading import Thread
import random
from sentence_transformers import SentenceTransformer, util
import requests
import torch
import numpy as np
import hashlib
import re
import time
from typing import List, Dict, Any
from collections import Counter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

HF_API_TOKEN = os.getenv('HF_API_TOKEN')
HF_API_URL = "https://router.huggingface.co/hf-inference/models/sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
headers = {
    "Authorization": f"Bearer {HF_API_TOKEN}",
}

flask_app = Flask(__name__)
CORS(flask_app)

class RouteExplainer:
    def __init__(self, api_token=None, model_name="IlyaGusev/saiga_llama3_8b:featherless-ai"):
        self.model_name = model_name
        self.api_token = api_token
        self.api_url = "https://router.huggingface.co/v1/chat/completions"
        self._cache = {}
        self._cached_prompts = self._precompile_prompts()
        self._category_mapping = {
            '1': 'Памятники и скульптуры',
            '2': 'Парки и природные объекты', 
            '3': 'Тактильные макеты',
            '4': 'набережные',
            '5': 'архитектура и исторические здания',
            '6': 'общественные центры',
            '7': 'музеи',
            '8': 'театры и филармонии',
            '10': 'монументальное искусство',
            '11': 'рестораны и кафе',
            '12': 'кофейни', 
            '13': 'кондитерские и пекарни',
            '14': 'торговые центры',
            '15': 'места для развлечений'
        }
        
        self._fallback_reasons = {
            '1': "выбран потому что это исторический памятник, отражающий культурное наследие города",
            '2': "включен в маршрут как природный объект для отдыха и прогулок", 
            '3': "добавлен как доступный макет для тактильного ознакомления",
            '4': "выбран из-за живописной набережной с красивыми видами",
            '5': "включен как архитектурная достопримечательность с богатой историей",
            '6': "добавлен как общественное пространство для мероприятий и отдыха",
            '7': "выбран потому что это музей с интересными экспозициями",
            '8': "включен как культурное учреждение для досуга и развлечений",
            '10': "добавлен как произведение монументального искусства",
            '11': "выбран как заведение для полноценного питания и отдыха",
            '12': "включен как уютное место для кофе-брейка и встреч",
            '13': "добавлен как кондитерская со свежей выпечкой и сладостями", 
            '14': "выбран как торговый комплекс с разнообразными магазинами",
            '15': "включен как развлекательное заведение для активного отдыха"
        }
        
        self._russian_pattern = re.compile(r'^[а-яА-ЯёЁ0-9\s\.,!?;-]+$')
    
    def _query_huggingface(self, prompt, max_retries=3):
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": "Ты — умный русскоязычный помощник по созданию туристических маршрутов."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 800,
            "temperature": 0.7,
            "top_p": 0.9,
        }

        for attempt in range(max_retries):
            try:
                response = requests.post(self.api_url, headers=headers, json=payload, timeout=120)
                if response.status_code == 200:
                    result = response.json()
                    if "choices" in result and len(result["choices"]) > 0:
                        return result["choices"][0]["message"]["content"]
                elif response.status_code == 503:
                    wait_time = (attempt + 1) * 30
                    print(f"⏳ Модель загружается, ждем {wait_time} секунд...")
                    time.sleep(wait_time)
                    continue
                else:
                    print(f"❌ Ошибка API: {response.status_code} - {response.text}")
                    if response.status_code in [400, 401, 404]:
                        break
            except requests.exceptions.Timeout:
                print(f"⏰ Таймаут запроса (попытка {attempt + 1})")
                continue
            except Exception as e:
                print(f"💥 Ошибка при запросе к API: {e}")
                continue

        return ""
    
    def _precompile_prompts(self):
        base_prompt = """Ты - помощник для создания туристических маршрутов. Создай связный маршрут по Нижнему Новгороду. ОБЯЗАТЕЛЬНО ИСПОЛЬЗУЙ ТОЛЬКО РУССКИЙ ЯЗЫК.

Доступные места для посещения:
{places}

Интересы пользователя: {interests}
Общее время маршрута: {duration} минут
Начальная точка: {location}

Создай маршрут, который логически соединяет эти места. Для каждого места дай КРАТКОЕ объяснение на РУССКОМ языке - почему именно оно было выбрано с учетом интересов пользователя и категории места.

Верни ответ ТОЛЬКО в формате JSON без каких-либо дополнительных пояснений:
{{
"route_name": "креативное название маршрута на русском",
"total_duration": общее_время,
"timeline": "краткое описание временного плана",
"explanation": "общее объяснение выбора маршрута",
"places": [
  {{
    "name": "название места",
    "order": 1,
    "duration": 30,
    "reason": "объяснение почему выбрано это место с учетом интересов пользователя"
  }}
]
}}"""
        return {'base': base_prompt}
    
    def _is_russian_text(self, text):
        if not text or not isinstance(text, str):
            return False
        sample = text[:100]
        return bool(self._russian_pattern.match(sample.replace('"', '').replace("'", "")))
    
    def _clean_russian_text(self, text):
        if not text:
            return ""
        cleaned = re.sub(r'[^а-яА-ЯёЁ0-9\s\.,!?;-]', '', str(text))
        return cleaned.strip()
    
    def _map_category(self, category_id):
        return self._category_mapping.get(str(category_id), 'достопримечательность')
    
    def _get_fallback_reason(self, place, user_interests):
        category_id = str(place.get('category_id', ''))
        base_reason = self._fallback_reasons.get(category_id, "выбрано как интересное место для посещения")
        
        if user_interests:
            interests_str = ' '.join(user_interests).lower()
            
            if any(word in interests_str for word in ['истори', 'музей', 'памятник']):
                if category_id in ['1', '5', '7']:
                    return f"выбран потому что соответствует вашему интересу к истории: {base_reason}"
                    
            elif any(word in interests_str for word in ['еда', 'кухн', 'ресторан', 'кофе', 'питание']):
                if category_id in ['11', '12', '13']:
                    return f"включен как гастрономическое место, соответствующее вашим интересам: {base_reason}"
                    
            elif any(word in interests_str for word in ['покуп', 'шоппинг', 'торгов']):
                if category_id == '14':
                    return f"добавлен для шопинга по вашему запросу: {base_reason}"
                    
            elif any(word in interests_str for word in ['развлек', 'отдых', 'досуг', 'кино']):
                if category_id in ['15', '2', '6']:
                    return f"выбран для развлечений и отдыха: {base_reason}"
        
        return base_reason

    def create_route(self, places, user_interests, total_duration, current_location):
        cache_key = self._generate_cache_key(places, user_interests, total_duration, current_location)
        
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        places_text = self._format_places_optimized(places)
        
        prompt = self._create_optimized_prompt(places_text, user_interests, total_duration, current_location)
        
        print(f"📝 Отправляем промпт в модель...")
        
        try:
            response_text = self._query_huggingface(prompt)
            
            if response_text:
                print(f"✅ Получен ответ от модели: {response_text[:200]}...")
                result = self._parse_and_validate_response(response_text, places, user_interests)
            else:
                print("⚠️  Пустой ответ от модели, используем запасной вариант")
                result = self._get_optimized_fallback_route(places, user_interests, total_duration)
            
        except Exception as e:
            print(f"💥 Ошибка при создании маршрута: {e}")
            result = self._get_optimized_fallback_route(places, user_interests, total_duration)
        
        self._cache[cache_key] = result
        return result

    def _generate_cache_key(self, places, user_interests, total_duration, current_location):
        places_hash = hashlib.md5(
            ''.join(sorted([p.get('name', '') + str(p.get('category_id', '')) for p in places])).encode()
        ).hexdigest()[:8]
        
        interests_hash = hashlib.md5(
            str(sorted(user_interests)).encode()
        ).hexdigest()[:6]
        
        return f"{places_hash}_{interests_hash}_{total_duration}"

    def _format_places_optimized(self, places):
        if not places:
            return "Нет доступных мест"
            
        formatted_places = []
        for i, p in enumerate(places[:5], 1):
            place_name = p.get('name', f'Место {i}')
            category_id = str(p.get('category_id', ''))
            category_name = self._map_category(category_id)
            
            place_str = f"{i}. {place_name} ({category_name})"
            formatted_places.append(place_str)
        
        return "\n".join(formatted_places)

    def _create_optimized_prompt(self, places_text, user_interests, total_duration, current_location):
        prompt_template = self._cached_prompts['base']
        
        return prompt_template.format(
            places=places_text,
            interests=user_interests,
            duration=total_duration,
            location=current_location
        )

    def _parse_and_validate_response(self, response_text, places, user_interests):
        print(f"🔍 Парсим ответ модели...")
        
        start = response_text.find('{')
        end = response_text.rfind('}') + 1
        
        if start == -1 or end == 0:
            print("❌ Не найден JSON в ответе")
            return self._get_optimized_fallback_route(places, user_interests, 120)
        
        try:
            json_str = response_text[start:end]
            print(f"📄 Найден JSON: {json_str[:200]}...")
            
            result = json.loads(json_str)
            
            if 'places' not in result or not isinstance(result['places'], list):
                print("❌ Некорректная структура JSON")
                return self._get_optimized_fallback_route(places, user_interests, 120)
            
            if 'route_name' in result:
                if not self._is_russian_text(result['route_name']):
                    result['route_name'] = self._generate_route_name(places, user_interests)
                else:
                    result['route_name'] = self._clean_russian_text(result['route_name'])
            
            valid_places = []
            for i, place in enumerate(result['places'][:4], 1):
                if 'name' not in place:
                    continue
                    
                place['name'] = self._clean_russian_text(place.get('name', f'Место {i}'))
                
                if 'reason' not in place or not self._is_russian_text(place['reason']):
                    original_place = next((p for p in places if p.get('name') == place['name']), None)
                    place['reason'] = self._get_fallback_reason(original_place, user_interests) if original_place else "выбрано как интересное место для посещения"
                else:
                    place['reason'] = self._clean_russian_text(place['reason'])
                
                place['order'] = i
                place['duration'] = place.get('duration', 30)
                
                valid_places.append(place)
            
            if not valid_places:
                print("❌ Нет валидных мест в маршруте")
                return self._get_optimized_fallback_route(places, user_interests, 120)
            
            result['places'] = valid_places
            
            # ИСПРАВЛЕНИЕ: Ограничиваем максимальное время маршрута
            if 'total_duration' not in result:
                result['total_duration'] = sum(p.get('duration', 30) for p in valid_places)
            
            # Ограничиваем максимальное время 24 часами (1440 минут)
            result['total_duration'] = min(result['total_duration'], 1440)
            
            if 'timeline' not in result:
                result['timeline'] = f"Маршрут из {len(valid_places)} мест"
            else:
                result['timeline'] = self._clean_russian_text(result['timeline'])
                
            if 'explanation' not in result:
                result['explanation'] = "Маршрут составлен с учетом ваших интересов"
            else:
                result['explanation'] = self._clean_russian_text(result['explanation'])
            
            print("✅ Маршрут успешно сформирован")
            return result
            
        except (json.JSONDecodeError, KeyError) as e:
            print(f"❌ Ошибка парсинга JSON: {e}")
            return self._get_optimized_fallback_route(places, user_interests, 120)

    def _get_optimized_fallback_route(self, places, user_interests, total_duration):
        print("🔄 Используем запасной вариант маршрута")
        
        if not places:
            return self._get_minimal_fallback_route()
        
        selected_places = places[:4]
        
        # ИСПРАВЛЕНИЕ: Защита от деления на ноль
        if len(selected_places) == 0:
            return self._get_minimal_fallback_route()
            
        place_duration = max(25, total_duration // len(selected_places))
        
        route_places = []
        for i, place in enumerate(selected_places, 1):
            route_places.append({
                "name": self._clean_russian_text(place.get('name', f'Место {i}')),
                "order": i,
                "duration": place_duration,
                "reason": self._get_fallback_reason(place, user_interests)
            })
        
        route_name = self._generate_route_name(selected_places, user_interests)
        
        return {
            "route_name": route_name,
            "total_duration": min(place_duration * len(route_places), 1440),  # Ограничение 24 часа
            "places": route_places,
            "timeline": f"Посещение {len(route_places)} мест",
            "explanation": f"Маршрут составлен автоматически с учетом ваших интересов: {', '.join(user_interests) if user_interests else 'основные достопримечательности'}"
        }

    def _generate_route_name(self, places, user_interests):
        if not places:
            return "Обзорный маршрут по Нижнему Новгороду"
        
        categories = [str(p.get('category_id', '')) for p in places if p.get('category_id')]
        
        category_themes = {
            '1': "Исторический",
            '2': "Природный",
            '5': "Архитектурный", 
            '7': "Музейный",
            '11': "Гастрономический",
            '12': "Кофейный",
            '13': "Кондитерский",
            '14': "Шопинг",
            '15': "Развлекательный"
        }
        
        if categories:
            most_common = Counter(categories).most_common(1)[0][0]
            if most_common in category_themes:
                return f"{category_themes[most_common]} маршрут по Нижнему Новгороду"
        
        if user_interests:
            interests_str = ' '.join(user_interests).lower()
            if any(word in interests_str for word in ['истори', 'музей']):
                return "Исторический маршрут по городу"
            elif any(word in interests_str for word in ['еда', 'кухн', 'ресторан', 'кофе']):
                return "Гастрономический маршрут"
            elif any(word in interests_str for word in ['покуп', 'шоппинг']):
                return "Торговый маршрут"
            elif any(word in interests_str for word in ['развлек', 'отдых']):
                return "Развлекательный маршрут"
        
        return "Обзорный маршрут по Нижнему Новгороду"

    def _get_minimal_fallback_route(self):
        return {
            "route_name": "Базовый маршрут по городу",
            "total_duration": 90,
            "places": [
                {
                    "name": "Центральные достопримечательности",
                    "order": 1,
                    "duration": 90,
                    "reason": "выбраны для обзора главных мест города"
                }
            ],
            "timeline": "Прогулка по центру",
            "explanation": "Рекомендуется уточнить интересующие места для детального маршрута"
        }

# Инициализация RouteExplainer
route_explainer = RouteExplainer(api_token=HF_API_TOKEN)

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
        print(f"✅ Датасет загружен: {len(ds)} записей")  # ОТЛАДКА
        return ds
    except Exception as e:
        print(f"❌ Ошибка загрузки датасета - {e}")  # ОТЛАДКА
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

def get_embeddings(texts):
    if not HF_API_TOKEN:
        print("❌ Ошибка: HF_API_TOKEN не установлен")  # ОТЛАДКА
        return None
        
    if isinstance(texts, str):
        texts = [texts]
    
    try:
        print(f"🔄 Отправляем запрос к Sentence Transformer API для {len(texts)} текстов")  # ОТЛАДКА
        response = requests.post(
            HF_API_URL,
            headers=headers,
            json={"inputs": texts, "options": {"wait_for_model": True}},
            timeout=30
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Успешно получены эмбеддинги от Sentence Transformer")  # ОТЛАДКА
            if isinstance(data, list) and isinstance(data[0], dict) and "embedding" in data[0]:
                return [item["embedding"] for item in data]
            return data
        else:
            logger.error(f"❌ Ошибка Sentence Transformer API: {response.status_code} - {response.text}")  # ОТЛАДКА
            return None
    except Exception as e:
        logger.error(f"❌ Исключение при запросе к Sentence Transformer API: {e}")  # ОТЛАДКА
        return None

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
    
def load_category_embeddings():
    print("🔄 Загружаем эмбеддинги категорий...")  # ОТЛАДКА
    embeddings = get_embeddings(category_names)
    if embeddings:
        print(f"✅ Эмбеддинги категорий загружены, размер: {len(embeddings)}")  # ОТЛАДКА
        return torch.tensor(embeddings)
    else:
        logger.error("❌ Не удалось получить эмбеддинги категорий")  # ОТЛАДКА
        return None

category_embeddings = load_category_embeddings()

def define_categories(text, similarity_threshold=0.5, min_categories=3, max_categories=5):
    print(f"🎯 Определяем категории для запроса: '{text}'")  # ОТЛАДКА
    
    if category_embeddings is None:
        print("❌ Эмбеддинги категорий не загружены")  # ОТЛАДКА
        return []
    
    query_emb = get_embeddings(text)
    if not query_emb:
        print("❌ Не удалось получить эмбеддинг запроса")  # ОТЛАДКА
        return []
    
    query_emb = torch.tensor(query_emb)
    similarities = util.cos_sim(query_emb, category_embeddings)[0]

    sorted_indices = torch.argsort(similarities, descending=True).tolist()
    sorted_scores = similarities[sorted_indices].tolist()

    found=[]

    for idx, score in zip(sorted_indices, sorted_scores):
        if score >= similarity_threshold:
            found.append((idx+1, score))
        if len(found) >= max_categories:
            break

    if len(found) < min_categories:
        for idx, score in zip(sorted_indices, sorted_scores):
            if (idx + 1, score) not in found:
                found.append((idx + 1, score))
            if len(found) >= min_categories:
                break

    print(f"🎯 Найдены категории для '{text}': {found}")  # ОТЛАДКА
    return found[:max_categories]

def get_candidate_places(query, ds):
    print(f"🔍 Ищем кандидаты для запроса: '{query}'")  # ОТЛАДКА
    top_categories_with_score = define_categories(query)
    top_categories_ids=[cid for cid, score in top_categories_with_score]
    
    # ИСПРАВЛЕНИЕ: Защита от пустого списка категорий
    if not top_categories_ids:
        print("⚠️ Не найдено подходящих категорий, используем случайные места")  # ОТЛАДКА
        # Возвращаем случайные места из датасета
        if ds is not None and len(ds) > 0:
            return ds.sample(min(5, len(ds))).copy()
        else:
            return pd.DataFrame()
    
    candidate_places=ds[ds['category_id'].isin(top_categories_ids)].copy()
    score_dict = {cid: score for cid, score in top_categories_with_score}
    candidate_places['score']=candidate_places['category_id'].apply(lambda x: score_dict.get(x, 0))
    
    print(f"📍 Найдено кандидатов: {len(candidate_places)}")  # ОТЛАДКА
    return candidate_places

categories_time = {
    1 : 15,
    2: 40,
    3: 15,
    4: 40,
    5: 30,
    6: 40,
    7: 40,
    8: 120,
    9: 10,
    10: 15,
    11: 40,
    12: 30,
    13: 15,
    14: 40,
    15: 60
}

@flask_app.route('/generate_route', methods=['POST', 'OPTIONS'])
def generate_route():
    logger.info("🚀 generate_route called")  # ОТЛАДКА

    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        return response

    try:
        data = request.get_json()
        if not data:
            print("❌ Нет JSON данных в запросе")  # ОТЛАДКА
            return jsonify({'error': 'No JSON data provided'}), 400

        query = data.get('query')
        hours = data.get('hours')
        minutes = data.get('minutes')
        startPoint = data.get('startPoint')

        print(f"📨 Получен запрос: query='{query}', hours={hours}, minutes={minutes}, startPoint='{startPoint}'")  # ОТЛАДКА

        if not query:
            print("❌ Отсутствует query в запросе")  # ОТЛАДКА
            return jsonify({'error': 'Query is required'}), 400

        # ИСПРАВЛЕНИЕ: Правильное преобразование времени
        try:
            hours = int(hours) if hours is not None else 0
            minutes = int(minutes) if minutes is not None else 0
            total_minutes = hours * 60 + minutes
            if total_minutes <= 0:
                total_minutes = 180  # Значение по умолчанию 3 часа
        except (ValueError, TypeError) as e:
            print(f"⚠️ Ошибка преобразования времени: {e}, используем значение по умолчанию")  # ОТЛАДКА
            total_minutes = 180  # Значение по умолчанию 3 часа

        print(f"⏱ Рассчитано общее время: {total_minutes} минут")  # ОТЛАДКА

        request_categories = define_categories(query)
        print(f"🎯 Найденные категории: {request_categories}")  # ОТЛАДКА

        ds = load_dataset()
        if ds is None:
            print("❌ Не удалось загрузить датасет")  # ОТЛАДКА
            return jsonify({'error': 'Failed to load dataset'}), 500

        # ИСПРАВЛЕНИЕ: Защита от пустого датасета
        if len(ds) == 0:
            print("❌ Датасет пустой")  # ОТЛАДКА
            return jsonify({'error': 'Dataset is empty'}), 500

        # Получаем кандидатов для маршрута
        candidate_places = get_candidate_places(query, ds)
        
        # ИСПРАВЛЕНИЕ: Защита от пустого списка кандидатов
        if candidate_places.empty:
            print("⚠️ Нет подходящих мест, используем случайные из датасета")  # ОТЛАДКА
            candidate_places = ds.sample(min(5, len(ds))).copy()
        
        print(f"📍 Отобрано кандидатов для маршрута: {len(candidate_places)}")  # ОТЛАДКА
        
        # Преобразуем в формат для RouteExplainer
        places_for_explainer = []
        for _, place in candidate_places.head(10).iterrows():  # Берем топ-10 мест
            places_for_explainer.append({
                'name': place['title'],
                'description': place.get('description', ''),
                'category_id': place['category_id'],
                'visit_duration': categories_time.get(place['category_id'], 30)
            })

        print(f"🔄 Подготовлено мест для RouteExplainer: {len(places_for_explainer)}")  # ОТЛАДКА
        
        # Используем RouteExplainer для создания маршрута
        route = route_explainer.create_route(
            places=places_for_explainer,
            user_interests=[query],
            total_duration=total_minutes,
            current_location=startPoint
        )

        print(f"🗺 RouteExplainer вернул маршрут: {route['route_name']}")  # ОТЛАДКА
        
        # Формируем ответ в нужном формате
        result_places = []
        for place in route['places']:
            # Находим соответствующее место в датасете
            original_place = candidate_places[candidate_places['title'] == place['name']]
            if not original_place.empty:
                original_place = original_place.iloc[0]
                try:
                    coords = original_place['coordinate'].replace("POINT(", "").replace(")", "").split()
                    result_places.append({
                        "title": original_place['name'],
                        "address": original_place['address'],
                        "coord": [float(coords[0]), float(coords[1])],
                        "description": original_place.get('description', ''),
                        "reason": original_place['reason'],
                        "time": original_place['duration']
                    })
                except Exception as e:
                    print(f"⚠️ Ошибка обработки координат для {place['name']}: {e}")  # ОТЛАДКА
                    # Добавляем место без координат
                    result_places.append({
                        "title": place['name'],
                        "address": original_place.get('address', ''),
                        "coord": [56.326887, 44.005986],  # Координаты по умолчанию (центр НН)
                        "description": original_place.get('description', ''),
                        "reason": place['reason'],
                        "time": place['duration']
                    })

        # ИСПРАВЛЕНИЕ: Человеко-читаемый формат времени
        total_h = route['total_duration'] // 60
        total_m = route['total_duration'] % 60
        totalTime = f"{total_h} ч {total_m} мин"

        result = {
            "startPoint": startPoint,
            "places": result_places,
            "totalTime": totalTime,
            "route_name": route.get('route_name', 'Маршрут по Нижнему Новгороду'),
            "explanation": route.get('explanation', ''),
            "timeline": route.get('timeline', '')
        }

        print(f"✅ Успешно сформирован ответ: {len(result_places)} мест, время: {totalTime}")  # ОТЛАДКА
        response = jsonify(result)
        return response

    except Exception as e:
        logger.error(f"💥 Критическая ошибка в generate_route: {str(e)}")  # ОТЛАДКА
        import traceback
        traceback.print_exc()  # Печать полного стека вызовов
        return jsonify({'error': 'Internal server error'}), 500

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
        
    logger.info("Bot is running from Render.com")

    Thread(target=lambda: flask_app.run(host="0.0.0.0", port=port, debug=False)).start()
        
    app.run_polling()

if __name__ == "__main__":
    main()

