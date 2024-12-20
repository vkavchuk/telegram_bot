from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from googletrans import Translator
import asyncio

API_TOKEN = '8101662681:AAHcWs0j798OYox7ul8c34ypJ3FNJy1CBj0'

ADMIN_USER_ID = [713895304, 821231747]  

# Initialize the bot
translator = Translator()
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Dictionary for storing user-selected language
user_language = {}

# Inline keyboard for language selection
language_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🇺🇦 Українська ❤️", callback_data="lang_ua")],
    [InlineKeyboardButton(text="🇩🇪 Deutsch 🌍", callback_data="lang_de")],
    [InlineKeyboardButton(text="🇬🇧 English 💬", callback_data="lang_en")]
])

TRIP_PHOTOS = {
    "france": None,  # Initially empty; updated via admin commands
    "amsterdam": None
}

# Trip-specific FAQs
TRIP_FAQ = {
    "france": {
        "ua": "❓ Часті запитання про Францію:\n- Які визначні місця ми відвідаємо?\n- Що включено у вартість поїздки?\n- Чи потрібна віза для подорожі?",
        "de": "❓ Häufig gestellte Fragen zu Frankreich:\n- Welche Sehenswürdigkeiten besuchen wir?\n- Was ist im Reisepreis enthalten?\n- Wird ein Visum benötigt?",
        "en": "❓ FAQs about France:\n- What landmarks will we visit?\n- What is included in the trip cost?\n- Do I need a visa for this trip?"
    },
    "amsterdam": {
        "ua": "❓ Часті запитання про Амстердам:\n- Чи буде вільний час для прогулянок?\n- Що таке Заансе-Сханс?\n- Де розташований готель?",
        "de": "❓ Häufig gestellte Fragen zu Amsterdam:\n- Gibt es Freizeit für Spaziergänge?\n- Was ist Zaanse Schans?\n- Wo befindet sich das Hotel?",
        "en": "❓ FAQs about Amsterdam:\n- Will there be free time for walks?\n- What is Zaanse Schans?\n- Where is the hotel located?"
    }
}


# Texts for different languages
TEXTS = {
    "start": {
        "ua": "🌍 Оберіть мову:",
        "de": "🌍 Wählen Sie eine Sprache:",
        "en": "🌍 Choose a language:"
    },
    "menu": {
        "ua": "✅ Мову обрано! Головне меню:",
        "de": "✅ Sprache ausgewählt! Hauptmenü:",
        "en": "✅ Language selected! Main menu:"
    },
    "back": {
        "ua": "⬅️ Назад",
        "de": "⬅️ Zurück",
        "en": "⬅️ Back"
    },
    "faq": {
        "ua": "❓ Відповіді на запитання:\n- Як забронювати поїздку?\n- Як відправити посилку?\nНапишіть в наш Telegram для більше інформації.",
        "de": "❓ Häufig gestellte Fragen:\n- Wie buche ich eine Reise?\n- Wie sende ich ein Paket?\nSchreiben Sie uns auf Telegram für weitere Informationen.",
        "en": "❓ FAQ:\n- How to book a trip?\n- How to send a parcel?\nMessage us on Telegram for more details."
    },
    "countries": {
        "ua": "Оберіть країну, яка вас цікавить для подорожі:",
        "de": "Wählen Sie ein Land für Ihre Reise:",
        "en": "Choose a country for your trip:"
    },
    "trip_info": {
        "france": {
            "ua": "🇫🇷 Подорож до Франції\n10-13.11.2023\nПрограма: ... (деталі поїздки)",
            "de": "🇫🇷 Reise nach Frankreich\n10-13.11.2023\nProgramm: ... (Reisedetails)",
            "en": "🇫🇷 Trip to France\n10-13.11.2023\nProgram: ... (trip details)"
        },
        "amsterdam": {
            "ua": "🇳🇱 Подорож до Амстердаму\n12-14.04.2024\nПрограма: ... (деталі поїздки)",
            "de": "🇳🇱 Reise nach Amsterdam\n12-14.04.2024\nProgramm: ... (Reisedetails)",
            "en": "🇳🇱 Trip to Amsterdam\n12-14.04.2024\nProgram: ... (trip details)"
        }
    }
}

# Create the main menu
def get_main_menu(lang):
    buttons = [
        [InlineKeyboardButton(text="🚍 Забронювати поїздку" if lang == "ua" else "🚍 Book a Trip" if lang == "en" else "🚍 Reise buchen", callback_data="book_trip")],
        [InlineKeyboardButton(text="📦 Відправлення посилки" if lang == "ua" else "📦 Send a Parcel" if lang == "en" else "📦 Paket senden", callback_data="send_parcel")],
        [InlineKeyboardButton(text="🌍 Подорожі в ЄС" if lang == "ua" else "🌍 Trips to EU" if lang == "en" else "🌍 Reisen in die EU", callback_data="eu_trips")],
        [InlineKeyboardButton(text="📅 Розклад маршрутів" if lang == "ua" else "📅 Schedule" if lang == "en" else "📅 Fahrplan", callback_data="schedule")],
        [InlineKeyboardButton(text="❓ Відповіді на запитання" if lang == "ua" else "❓ FAQ" if lang == "en" else "❓ FAQ", callback_data="faq_main")],
        [InlineKeyboardButton(text=TEXTS["back"][lang], callback_data="go_back")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# EU trips menu
def build_country_menu(lang):
    buttons = [
        [InlineKeyboardButton(text=f"🇫🇷 {TRIP_DATA['france'][lang]}", callback_data="france")],
        [InlineKeyboardButton(text=f"🇳🇱 {TRIP_DATA['amsterdam'][lang]}", callback_data="amsterdam")],
        [InlineKeyboardButton(text=TEXTS["back"][lang], callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# Country menu options
def get_trip_options(lang):
    buttons = [
        [InlineKeyboardButton(text="🚍 Забронювати подорож" if lang == "ua" else "🚍 Book a trip", callback_data="book_trip")],
        [InlineKeyboardButton(text="ℹ️ Кількість вільних місць" if lang == "ua" else "ℹ️ Available seats", callback_data="available_seats")],
        [InlineKeyboardButton(text="❓ Часті запитання" if lang == "ua" else "❓ FAQ", callback_data="trip_faq")],
        [InlineKeyboardButton(text=TEXTS["back"][lang], callback_data="eu_trips")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)



# Start command
@dp.message(F.text == "/start")
async def send_welcome(message: types.Message):
    lang = user_language.get(message.from_user.id, "en")  # Default to English
    await message.answer(TEXTS["start"][lang], reply_markup=language_kb)

# After updating the trip info
@dp.message(F.text.startswith("/update_trip") & F.from_user.id == ADMIN_USER_ID)
async def update_trip_info(message: types.Message):
    try:
        # Parse the command: `/update_trip france <info>`
        parts = message.text.split(" ", 2)
        if len(parts) < 3:
            await message.reply("❌ Usage: /update_trip <country_key> <new_info>")
            return

        country_key, new_info = parts[1], parts[2]

        # Check if the country key is valid
        if country_key not in TEXTS["trip_info"]:
            await message.reply("❌ Invalid country key. Use valid keys like 'france' or 'amsterdam'.")
            return

        # Translate the info into supported languages
        translations = {
            "ua": new_info,  # Original text is assumed to be in Ukrainian
            "de": translator.translate(new_info, src="uk", dest="de").text,
            "en": translator.translate(new_info, src="uk", dest="en").text
        }

        # Update trip info
        TEXTS["trip_info"][country_key] = translations
        await message.reply(f"✅ Trip info for {country_key.capitalize()} updated successfully with translations!")
    except Exception as e:
        await message.reply(f"❌ Error: {str(e)}")


@dp.message(F.photo & F.caption.startswith("/upload_photo") & F.from_user.id == ADMIN_USER_ID)
async def upload_trip_photo(message: types.Message):
    try:
        # Parse the command: `/upload_photo france`
        parts = message.caption.split(" ", 1)
        if len(parts) < 2:
            await message.reply("❌ Usage: Send a photo with caption: /upload_photo <country_key>")
            return

        country_key = parts[1]
        if country_key in TRIP_PHOTOS:
            # Save photo file_id for future use
            TRIP_PHOTOS[country_key] = message.photo[-1].file_id
            await message.reply(f"✅ Photo for {country_key.capitalize()} updated successfully!")
        else:
            await message.reply("❌ Invalid country key. Use valid keys like 'france' or 'amsterdam'.")
    except Exception as e:
        await message.reply(f"❌ Error: {str(e)}")


@dp.callback_query(F.data == "trip_faq")
async def show_trip_faq(callback: types.CallbackQuery):
    lang = user_language.get(callback.from_user.id, "en")
    trip_key = callback.message.text.split()[1].lower()  # Extract country from the message
    faq_text = TRIP_FAQ.get(trip_key, {}).get(lang, "No FAQs available for this trip.")
    await callback.message.edit_text(faq_text, reply_markup=get_trip_options(lang))


# Handle language selection
@dp.callback_query(F.data.startswith("lang_"))
async def set_language(callback: types.CallbackQuery):
    lang_map = {"lang_ua": "ua", "lang_de": "de", "lang_en": "en"}
    user_language[callback.from_user.id] = lang_map[callback.data]
    lang = user_language[callback.from_user.id]
    await callback.message.edit_text(TEXTS["menu"][lang], reply_markup=get_main_menu(lang))

# Handle FAQ
@dp.callback_query(F.data == "faq_main")
async def show_general_faq(callback: types.CallbackQuery):
    lang = user_language.get(callback.from_user.id, "en")
    await callback.message.edit_text(TEXTS["faq"][lang], reply_markup=get_main_menu(lang))


# Handle "Trips to EU"
@dp.callback_query(F.data == "eu_trips")
async def show_countries(callback: types.CallbackQuery):
    lang = user_language.get(callback.from_user.id, "en")
    await callback.message.edit_text(TEXTS["countries"][lang], reply_markup=build_country_menu(lang))

# Handle country selection
@dp.callback_query(F.data.in_(["france", "amsterdam"]))
async def show_trip_info(callback: types.CallbackQuery):
    lang = user_language.get(callback.from_user.id, "en")
    trip_info = TEXTS["trip_info"][callback.data][lang]
    photo_path = TRIP_PHOTOS[callback.data]  # Шлях до фото

    try:
        # Надсилаємо фото без підпису
        photo = types.InputFile(photo_path)
        await bot.send_photo(chat_id=callback.from_user.id, photo=photo)
        
        # Надсилаємо текст окремо
        await bot.send_message(chat_id=callback.from_user.id, text=trip_info)
    except Exception as e:
        # Обробляємо помилки
        await callback.message.answer(f"❌ Error: {str(e)}")



# Back to main menu
@dp.callback_query(F.data == "main_menu")
async def back_to_main_menu(callback: types.CallbackQuery):
    lang = user_language.get(callback.from_user.id, "en")
    await callback.message.edit_text(TEXTS["menu"][lang], reply_markup=get_main_menu(lang))

# Back to language selection
@dp.callback_query(F.data == "go_back")
async def go_back(callback: types.CallbackQuery):
    await callback.message.edit_text(TEXTS["start"]["en"], reply_markup=language_kb)

# Run the bot
async def main():
    print("Bot is running!")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
