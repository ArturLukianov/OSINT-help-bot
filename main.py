import telebot
import re
from flask import Flask, request
import os

TOKEN = os.environ.get('TELEGRAM_TOKEN')
server_url = os.environ.get('SERVER_URL')

bot = telebot.TeleBot(TOKEN)

# Handlers

@bot.message_handler(commands=['start'])
def start_handler(message):
    bot.send_message(message.chat.id, "Бот работает!")

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

