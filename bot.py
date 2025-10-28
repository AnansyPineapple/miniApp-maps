import os
import logging
import pandas as pd
import json
import random
import urllib.parse
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        [InlineKeyboardButton("Открыть приложение", web_app = {"url" : "https://abchihba0.github.io/miniApp/"})]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Привет, друг! Нажми кнопку ниже чтобы запустить приложение!", reply_markup = reply_markup)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Открыть приложение", web_app = {"url" : "https://abchihba0.github.io/miniApp/"})]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Чтобы начать работу необходимо запустить приложение!", reply_markup = reply_markup)

async def ai_run(user_request, hours, minutes, start_point):
    dataset = load_dataset()
    
    #Пока что берем рандомное кол-во мест от 3 до 5, и берем это число случайных мест
    n = random.randint(3, 5)
    places = random.sample(range(len(dataset)), n)
    result = []

    for i in places:
        place = dataset.iloc[i]

        point = str(place.get('coordinate', 'POINT (0 0)'))
        if 'POINT' in point:
            coords = place.replace('POINT (', '').replace(')', '')
            x, y = map(float, coords.split())
        else:
            x, y = 44.006516, 56.326797
        
        result.append({
            'id': place.get('id'),
            'title': place.get('title'),
            'address': place.get('address'),
            'description': place.get('description'),
            'coordinates': {'x': x, 'y': y},
            'url': place.get('url', ''),
            'reason': "Это место подходит под ваш запрос"
        })

        return result
    
async def handle_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    web_data = update.message.web_data
    data_json = web_data.data

    data = json.loads(data_json)

    user_request = data['user_request']
    hours = data['hours']
    minutes = data['minutes']
    start_point = data['start_point']

    answer = ai_run(user_request, hours, minutes, start_point)

    places_json = json.dumps(answer, ensure_ascii=False)
    encoded_places = urllib.parse.quote(places_json)

    answer_url = f"https://abchihba0.github.io/miniApp/answer.html?data={encoded_places}"

    keyboard = [
        [InlineKeyboardButton("Посмотреть маршрут", web_app={"url": answer_url})]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(f"Маршрут сгенерирован!\nНайдено {len(answer)} мест", reply_markup = reply_markup)

def main():
    token = get_bot_token()
    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.StatusUpdate.DATA, handle_data))

    if os.getenv('RENDER'):
        port = int(os.environ.get('PORT', 10000))
        webhook_url = os.getenv('WEBHOOK_URL')
        
        if not webhook_url:
            raise ValueError("WEBHOOK_URL was not set!")
        
        full_webhook_url = f"{webhook_url}/{token}"

        logger.info("Bot is running from Render.com")

        app.run_webhook(
            listen="0.0.0.0", 
            port=10000, 
            webhook_url=full_webhook_url,
            url_path=token
            )
        
    else:
        app.run_polling()
        logger.info("Bot is running locally")

if __name__ == "__main__":
    main()