import telebot
from telebot import types
import random

TOKEN = '8476874372:AAH-UT3WPl3cfJ0CddKYS68lmiRnCO9T25w'
bot = telebot.TeleBot(TOKEN)

# URL вашего веб-приложения (после деплоя)
WEB_APP_URL = "https://your-app-name.onrender.com"  # Или другой хостинг

user_stats = {}

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn1 = types.KeyboardButton("📍 Отправить геопозицию", request_location=True)
    btn2 = types.KeyboardButton("🗺 Открыть карту нарушений")
    btn3 = types.KeyboardButton("📸 Отправить фото нарушения")
    btn4 = types.KeyboardButton("🏆 Моя статистика")
    markup.add(btn1, btn2, btn3, btn4)

    bot.send_message(message.chat.id, 
                     f"🌿 Привет, {message.from_user.first_name}!\n\n"
                     f"Это эко-мониторинг Ижевска.\n"
                     f"Что вы хотите сделать?",
                     reply_markup=markup)

@bot.message_handler(content_types=['location'])
def handle_location(message):
    lat = message.location.latitude
    lon = message.location.longitude
    
    user_id = message.from_user.id
    user_stats[user_id] = user_stats.get(user_id, 0) + 1

    web_app_url = f"{WEB_APP_URL}/add?lat={lat}&lon={lon}&user_id={user_id}"
    
    inline_markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("📍 Добавить описание и фото", url=web_app_url)
    inline_markup.add(btn)

    response = (f"✅ Координаты получены!\n"
                f"📍 Широта: {lat:.6f}\n"
                f"📍 Долгота: {lon:.6f}\n\n"
                f"Нажмите кнопку ниже, чтобы добавить детали и фото к этой точке!")
    
    bot.send_message(message.chat.id, response, reply_markup=inline_markup)

@bot.message_handler(func=lambda message: message.text == "📸 Отправить фото нарушения")
def request_photo(message):
    bot.send_message(message.chat.id, 
                     "📸 Пожалуйста, отправьте фото нарушения. "
                     "После этого отправьте геопозицию для привязки фото к карте.")

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    # Сохраняем ID фото (само фото храним в Telegram)
    file_id = message.photo[-1].file_id
    
    ai_analysis = random.choice([
        "⚠️ Тип: Строительный мусор",
        "⚠️ Тип: Бытовые отходы",
        "⚠️ Тип: Загрязнение водоема",
        "⚠️ Тип: Несанкционированная свалка"
    ])
    
    bot.reply_to(message, 
                 f"🤖 ИИ-анализ:\n{ai_analysis}\n\n"
                 f"Фото получено (ID: {file_id[:10]}...)\n"
                 f"Теперь отправьте геопозицию, чтобы привязать его к карте!")

@bot.message_handler(func=lambda message: message.text == "🏆 Моя статистика")
def stats(message):
    count = user_stats.get(message.from_user.id, 0)
    level = "Новичок" if count < 3 else "Активист" if count < 10 else "Эко-герой"
    bot.send_message(message.chat.id, 
                     f"👤 Ваша статистика:\n\n"
                     f"📊 Отчетов создано: {count}\n"
                     f"🏅 Уровень: {level}\n"
                     f"🌱 Спасли {count * 10} м² природы")

@bot.message_handler(func=lambda message: message.text == "🗺 Открыть карту нарушений")
def open_map(message):
    inline_markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("🗺 Просмотреть все нарушения", url=WEB_APP_URL)
    btn2 = types.InlineKeyboardButton("📍 Добавить новое нарушение", url=f"{WEB_APP_URL}/add")
    inline_markup.add(btn1, btn2)
    
    bot.send_message(message.chat.id, 
                     "🗺 **Карта экологических нарушений Ижевска:**\n\n"
                     "Выберите действие:\n"
                     "• Просмотреть все метки\n"
                     "• Добавить новое нарушение\n\n"
                     "📱 Можно добавлять фото прямо с телефона!", 
                     reply_markup=inline_markup)

bot.polling(none_stop=True)