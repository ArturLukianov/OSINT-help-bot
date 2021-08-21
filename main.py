import telebot
import re
from flask import Flask, request
import os
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = os.environ.get('TELEGRAM_TOKEN')
server_url = os.environ.get('SERVER_URL')

bot = telebot.TeleBot(TOKEN)

# Markups

def gen_node_markup(node):
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    buttons = []
    for i, element in enumnerate(node):
        buttons.append(InlineKeyboardButton("OSINT", callback_data="node_id"))
    markup.add(*buttons)
    return markup

# Handlers

@bot.message_handler(commands=['start'])
def start_handler(message):
    try:
        bot.send_message(message.chat.id, "Чем я могу вам помочь?", reply_markup=gen_node_markup([1,2,3]), parse_mode='Markdown')
    except Exception as e:
        bot.send_message(message.chat.id, str(e))

# Server

server = Flask(__name__)

@server.route('/bot', methods=['POST'])
def getMessage():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "!", 200

@server.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url=server_url + "/bot")
    return "?", 200

