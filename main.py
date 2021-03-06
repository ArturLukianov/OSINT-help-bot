import telebot
import re
from flask import Flask, request
import os
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import json


TOKEN = os.environ.get('TELEGRAM_TOKEN')
server_url = os.environ.get('SERVER_URL')


root_node = json.load(open('arf.json'))

bot = telebot.TeleBot(TOKEN)

# Markups

def gen_node_markup(nodes, base_id):
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    buttons = []
    for i, node in enumerate(nodes):
        if node['type'] == 'folder':
            buttons.append(InlineKeyboardButton('📁 ' + node['name'], callback_data=base_id + "_" + str(i)))
        else:
            buttons.append(InlineKeyboardButton('🌐 ' + node['name'], url=node['url']))
    if base_id != 'i':
        buttons.append(InlineKeyboardButton('<<', callback_data='_'.join(base_id.split('_')[:-1])))
    markup.add(*buttons)
    return markup

def get_node(node, node_path):
    if node_path == []:
        return node
    return get_node(node['children'][node_path[0]], node_path[1:])

# Handlers

@bot.callback_query_handler(func=lambda call: True)
def callback_node(call):
    try:
        cid = call.message.chat.id
        mid = call.message.message_id
        node_id = call.data
        node_path = list(map(int, node_id.split('_')[1:]))

        node = get_node(root_node, node_path)
        
        bot.edit_message_text(chat_id=cid, message_id=mid, text=node['name'], reply_markup=gen_node_markup(node['children'], node_id), parse_mode='Markdown')
    except Exception as e:
        bot.send_message(cid, str(e))


@bot.message_handler(commands=['start'])
def start_handler(message):
    try:
        bot.send_message(message.chat.id, root_node['name'], reply_markup=gen_node_markup(root_node['children'], 'i'), parse_mode='Markdown')
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

