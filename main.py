import telebot
import pandas as pd
from telebot.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton
from translate import Translator

def language_to_code(lang_code):
    df = pd.read_csv('languages.csv')
    try:
        result = df.loc[df['Language'] == lang_code]['Code'].iloc[0]
        return result
    except IndexError:
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

SELECT_LANGUAGE, TRANSLATE_TEXT = range(2)
bot = telebot.TeleBot(token = '<token_string>')
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, f"Hi {message.from_user.first_name}, press /set_language to choose your preferred language.")

@bot.message_handler(commands=['set_language'])
def set_language(message):
    global available_languages, user_language
    df = pd.read_csv('languages.csv')
    available_languages = df['Language'].tolist()
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(*[KeyboardButton(lang) for lang in available_languages])
    bot.send_message(message.chat.id, "Choose your preferred language:", reply_markup=markup)
    bot.register_next_step_handler(message, handle_language_selection)
def handle_language_selection(message):
    global user_language
    user_language = message.text    
    if user_language in available_languages:
        reply = f"You selected {user_language}. Now, send the text you want to translate."
        bot.send_message(message.chat.id, reply)
        bot.register_next_step_handler(message, translate_message)
    else:
        bot.send_message(message.chat.id, "Invalid language selection. Please choose a language from the provided options or press /set_language")

def translate_message(message):
    global user_language
    if not user_language:
        bot.send_message(message.chat.id, "Please set your language first using /set_language command.")
        return
    dest = language_to_code(user_language)
    instance = Translator(config_path='config.yaml', target=dest)
    result,source = instance.translate(message.text)
    reply = f"{result} (from {source})"
    bot.send_message(message.chat.id, reply)
    add = "To Translate another text please choose langauge from /set_language"
    bot.send_message(message.chat.id, add)


@bot.message_handler(func=lambda message: True)
def handle_other_messages(message):
    bot.send_message(message.chat.id, "Invalid command. Press /set_language to choose your preferred language.")

# Start polling
bot.infinity_polling()
