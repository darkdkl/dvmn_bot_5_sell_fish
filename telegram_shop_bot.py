import os
import logging
import redis
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Filters, Updater
from telegram.ext import CallbackQueryHandler, CommandHandler, MessageHandler
import moltin_api
from db_redis_connect import get_database_connection


def start(bot, update):
    items = moltin_api.get_items()

    if update.message:

        chat_id = update.message.chat_id
    elif update.callback_query:

        chat_id = update.callback_query.message.chat_id
    else:
        return

    keyboard = []
    for item in items['data']:
        keyboard.append([InlineKeyboardButton(
            f"{item['name']}", callback_data=f"{item['id']}")])

    keyboard.append([InlineKeyboardButton("Корзина", callback_data='cart')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    bot.send_message(chat_id=chat_id, text='Список товаров:',
                     reply_markup=reply_markup)

    return "HANDLE_MENU"


def get_handle_menu(bot, update):
    query = update.callback_query
    chat_id = query.message.chat_id
    items = moltin_api.get_items(query.data)['data'][0]
    name = items['name']
    price = items['meta']['display_price']['with_tax']['formatted']
    amount = items['meta']['display_price']['with_tax']['amount']
    description = items['description']
    text = f'{name}\n{price} in Kg \n {amount} kg in stock \n {description}'
    keyboard = [[InlineKeyboardButton("1 kg", callback_data=f'1kg:{query.data}'),
                 InlineKeyboardButton("5 kg", callback_data=f'5kg:{query.data}'),
                 InlineKeyboardButton("10 kg", callback_data=f'10kg:{query.data}')],
                [InlineKeyboardButton("Назад", callback_data='/start')],
                [InlineKeyboardButton("Корзина", callback_data='cart')]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    
    bot.send_photo(
        chat_id=chat_id, photo=f'{moltin_api.get_image_url(query.data)}', caption=text, reply_markup=reply_markup)
    bot.delete_message(chat_id=chat_id,
                       message_id=query.message.message_id)
    return 'HANDLE_DESCRIPTION'


def get_handle_description(bot, update):
    query = update.callback_query
    weight,id_item = query.data.split(':')

    chat_id = query.message.chat_id
    if query.data == 'go_back':

        return 'START'

    if weight == '1kg':
        moltin_api.add_cart(id_item, 1, chat_id)

    elif weight == '5kg':
        moltin_api.add_cart(id_item, 5, chat_id)
    elif weight == '10kg':
        moltin_api.add_cart(id_item, 10, chat_id)


   
    return 'HANDLE_CART'
    
def get_cart(bot,update):

    query = update.callback_query
    chat_id = query.message.chat_id
    cart = moltin_api.get_items_cart(chat_id)
    items_in_cart = []
    for item in cart['data']:
        cart_info = []
        cart_info.append(item['name']+':\n')
        cart_info.append(item['description']+'\n')
        cart_info.append(item['meta']['display_price']
                         ['with_tax']['unit']['formatted'] + 'per kg \n')
        cart_info.append(str(item['quantity'])+'kg in cart for '+str(
            item['meta']['display_price']['with_tax']['value']['formatted'])+'\n\n')

        items_in_cart.append(cart_info)
    cart_bill = moltin_api.get_items_cart(chat_id, True)
    items_in_cart.append(
        'Total:'+str(cart_bill['data']['meta']['display_price']['with_tax']['formatted']))

    keyboard = []
    for item in cart['data']:
        
        keyboard.append([InlineKeyboardButton(
            f"Убрать из Корзины {item['name']}", callback_data=f"{item['id']}")])
    keyboard.append([InlineKeyboardButton("Оплатить", callback_data='pay')])
    keyboard.append([InlineKeyboardButton("в Меню", callback_data='/start')])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    items_in_cart_string=' '.join((map(' '.join, items_in_cart)))
    bot.send_message(chat_id=chat_id, text=items_in_cart_string,reply_markup=reply_markup) 
    return 'DELETE_FROM_CART'



def delete_from_cart(bot,update):
    
    
    query = update.callback_query
    chat_id = query.message.chat_id

   
    moltin_api.delete_item_from_cart(chat_id,query.data)
    bot.delete_message(chat_id=chat_id,
                       message_id=query.message.message_id)
    
    
def ask_email(bot,update):
    chat_id = update.callback_query.message.chat_id
    bot.send_message(chat_id=chat_id, text='''
    Для продолжения оформления заказа,сообщите своей e-mail''')

    return "WAITING_EMAIL"

def wait_email(bot,update):
    text=update.message.text
    full_name=update.message.chat.first_name+'\xa0'+update.message.chat.last_name
    if moltin_api.get_customer(moltin_api.create_customer(full_name,text)):
        message='Зарегистрирован новый покупатель,отдел продаж свяжется с Вами  в ближайшее время'
        
    else:
        message='Вы допустили ошибку при вводе e-mail,либо  такой пользователь существует'

    bot.send_message(chat_id=update.message.chat_id, text=message)

    return "WAITING_EMAIL"
    
    



def handle_users_reply(bot, update):

    db = get_database_connection()
    if update.message:
        user_reply = update.message.text

        chat_id = update.message.chat_id
    elif update.callback_query:

        user_reply = update.callback_query.data

        chat_id = update.callback_query.message.chat_id
    else:
        return
    
    if user_reply == '/start':
        user_state = 'START'
    elif user_reply == 'cart':
        user_state = 'HANDLE_CART'
    elif user_reply == 'pay':
        user_state = 'ASK_EMAIL'
    
    else:
        user_state = db.get(chat_id).decode("utf-8")

    states_functions = {
        'START': start,
        'HANDLE_MENU': get_handle_menu,
        'HANDLE_DESCRIPTION': get_handle_description,
        'DELETE_FROM_CART':delete_from_cart,
        'HANDLE_CART':get_cart,
        "ASK_EMAIL": ask_email,
        'WAITING_EMAIL':wait_email,
    
        
    }

    state_handler = states_functions[user_state]
    
    try:
        next_state = state_handler(bot, update)
        
        db.set(chat_id, next_state)
    except Exception as err:
        print(err)





if __name__ == '__main__':
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    updater = Updater(token)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CallbackQueryHandler(handle_users_reply))
    dispatcher.add_handler(MessageHandler(Filters.text, handle_users_reply))
    dispatcher.add_handler(CommandHandler('start', handle_users_reply))
    updater.start_polling()
