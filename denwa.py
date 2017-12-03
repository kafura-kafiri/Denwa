#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Simple Bot to reply to Telegram messages
# This program is dedicated to the public domain under the CC0 license.
"""
This Bot uses the Updater class to handle the bot.
First, a few callback functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Example of a bot-user conversation using ConversationHandler.
Send /start to initiate the conversation.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.

'503798742:AAHzfg7uqG8z6RU1p0C3ktRf0uPO2FNMb4Q'
#contact_keyboard = telegram.KeyboardButton(text="send_contact", request_contact=True)
"""
from auto_place import sug_place
from search import search
from config import ObjectId, users, pr, models
from ast import literal_eval
import telegram
from telegram import ReplyKeyboardMarkup
from telegram.ext import (Updater, CommandHandler, MessageHandler, CallbackQueryHandler, Filters, RegexHandler,
                          ConversationHandler)
from telegram.ext import Handler
import logging
import datetime
from utility import check_price

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

REQ, PUSH_MODEL, PUSH_PRICE, LOCATION, CONTACT, MY, PRODUCT, PRETTY_RANDOM_QUESTIONS = range(8)

# fuck callback_data is only supported with inline keyboard
listeners_key = telegram.KeyboardButton("/listeners", callback_data='/listeners')
push_key = telegram.KeyboardButton("/push", callback_data='/push')
my_key = telegram.KeyboardButton("/my", callback_data='/my')

reply_keyboard = [[listeners_key], [push_key, my_key]] #dakhele my khodesh halate delete daare.
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)


def start(bot, update, user_data):
    user_data['wish_list'] = []
    id = update.message.chat_id
    user = users.find_one({'id': id})
    if user:
        user_data.update(user)
    update.message.reply_text("Hi! i am digidooniBot", reply_markup=markup)
    return REQ


def req(bot, update, user_data):
    text = update.message.text
    result = search(text, 1, 5)
    for idx, model in enumerate(result):
        keyboard = [[telegram.InlineKeyboardButton(model['title']['compact'], callback_data=str(model['_id']))]]
        reply_markup = telegram.InlineKeyboardMarkup(keyboard)
        update.message.reply_text(
            str(idx) + ') ' + model['title']['fa'],
            reply_markup=reply_markup
        )
    user_data.pop('query', None)
    if 'state' in user_data:
        state = user_data['state']
        del user_data['state']
        return state
    return REQ


def add_listener(bot, update, user_data):
    if 'query' not in user_data:
        query = update.callback_query
        user_data['query'] = query
        user_data['wish_list'].append(query.data)
    if 'location' not in user_data:
        user_data['redirect'] = add_listener
        return location_get(bot, query, user_data)
    query = user_data['query']
    if 'redirect' in user_data:
        user_data['redirect'](bot, update, user_data)
    query.message.reply_text(
        query.data
    )
    # TODO loop of pr search and optimizer.
    return REQ


def location_get(bot, update, user_data):
    location_keyboard = telegram.KeyboardButton("send_location", request_location=True)
    reply_markup = telegram.ReplyKeyboardMarkup([[location_keyboard]], one_time_keyboard=True, resize_keyboard=True)
    update.message.reply_text(
        text=
        "Would you mind sharing your location?"
        "it's more accurate to give your location but you can say just your city also",
        reply_markup=reply_markup
    )
    return LOCATION


def location_post(bot, update, user_data):
    if 'location' in update.message:
        location = literal_eval(str(update.message.location))
    if 'text' in update.message:
        text = update.message.text
        if 'part_of_location' in user_data:
            text += ' ' + user_data['part_of_location']
            del user_data['part_of_location']
        _local, _global = sug_place(text)
        if len(_local) == 1:
            update.message.reply_text('did u mean:' + _local[0])
            # TODO add inline button
            user_data['locations'] = _local
            return LOCATION
        if len(_local) > 1:
            if len(_local) < 5:
                for place in _local:
                    update.message.reply_text(place)
                    # TODO add inline button
                    user_data['locations'] = _local
                    return LOCATION
            else:
                update.message.reply_text('complete it')
                user_data['part_of_location'] = text
                return LOCATION
        if _global:
            update.message.reply_text('complete it')
            user_data['part_of_location'] = text
            return LOCATION
        else:
            update.message.reply_text('wtf try again insert a place')
            return LOCATION
    else:
        query = update.callback_query
        locations = user_data['locations']
        location = locations[int(query.data)]
        location = location['location']

    # text # complete with google api > get lat lang
    # {'longitude': 51.31218, 'latitude': 35.722753}
    user_data['location'] = location
    update.message.reply_text('thanks for your location', reply_markup=markup)
    if 'redirect' in user_data:
        return user_data['redirect'](bot, update, user_data)
    return REQ


def push_model_get(bot, update, user_data):
    if 'location' not in user_data:
        user_data['redirect'] = push_model_get
        return location_get(bot, update, user_data)
    if 'contact' not in user_data:
        user_data['redirect'] = push_model_get
        return contact_get(bot, update, user_data)
    update.message.reply_text('insert model or you can type @denwabot ')
    user_data['state'] = PUSH_MODEL
    return PUSH_MODEL


def contact_get(bot, update, user_data):
    contact_keyboard = telegram.KeyboardButton(text="send_contact", request_contact=True)
    reply_markup = telegram.ReplyKeyboardMarkup([[contact_keyboard]], one_time_keyboard=True, resize_keyboard=True)
    update.message.reply_text(
        text=
        "or share your contact"
        "please put your number eg.09133657623",
        reply_markup=reply_markup
    )
    return CONTACT


def contact_push(bot, update, user_data):
    text = update.message.text
    contact = update.message.contact
    user_data['contact'] = contact['phone_number'] if contact else text
    update.message.reply_text('thanks', reply_markup=markup)
    if 'redirect' in user_data:
        return user_data['redirect'](bot, update, user_data)
    return REQ


def push_model_post(bot, update, user_data):
    query = update.callback_query
    user_data['model'] = query.data
    update.message.reply_text(
        'now give us your price'
        'please make sure your price is correct'
        'dimension is toman'
        'eg. ۸,۰۰۰ = هشت هزار تومان'
    )
    return PUSH_PRICE


def push_price(bot, update, user_data):
    text = update.message.text
    if not text:
        return error(bot, update, user_data)
    if 'model' not in user_data:
        update.message.reply_text('so where the hell your model gone')
        return push_model_get(bot, update, user_data)
    model = models.find_one({'_id': user_data['model']})
    price_validity, message = check_price(text, model['price'])
    if not price_validity:
        update.message.reply_text(message)
        return PUSH_PRICE
    update.message.reply_text(message)
    data = {
        '_author': update.message.chat_id,
        '_date': datetime.datetime.now(),
        'model': model,
        'price': text,
        'location': user_data['location'],
        'contact': user_data['contact'],
    }
    import json
    update.message.reply_text(
        'congrats'
        'your_pr: ' + str(data)
    )
    pr.insert_one(data)
    return REQ


def my_pr(bot, update, user_data):
    _id = update.message.chat_id
    _pr = pr.find({'_author': _id})
    keyboard = []
    for p in _pr:
        if len(keyboard) == 0 or len(keyboard[-1]) == 3:
            keyboard.append([])
        key_line = keyboard[-1]
        key_line.append(telegram.InlineKeyboardButton(p['model'], callback_data=str(p['_id'])))
    keyboard.append([telegram.InlineKeyboardButton('back', callback_data='/back')])
    reply_markup = telegram.InlineKeyboardMarkup(keyboard)
    update.message.reply_text(
        'your pr:',
        reply_markup=reply_markup
    )
    return MY


def product_get(bot, update, user_data):
    query = update.callback_query
    action = query.data
    if action == '/back':
        bot.delete_message(chat_id=query.message.chat_id, message_id=query.message.message_id)
        return REQ
    _id = action
    remove = telegram.InlineKeyboardButton('remove', callback_data=str(_id))
    back = telegram.InlineKeyboardButton('back', callback_data='/back')
    reply_markup = telegram.InlineKeyboardMarkup([[remove, back]])
    bot.edit_message_text(
        text="Selected option: {}".format(_id),
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        reply_markup=reply_markup
    )
    return PRODUCT


def product_post(bot, update, user_data):
    query = update.callback_query
    action = query.data
    if action != '/back':
        _id = ObjectId(action)
        pr.delete_one({'_id': _id})
    _pr = pr.find({'_author': query.message.chat_id})
    keyboard = []
    for p in _pr:
        if len(keyboard) == 0 or len(keyboard[-1]) == 3:
            keyboard.append([])
        key_line = keyboard[-1]
        key_line.append(telegram.InlineKeyboardButton(p['model'], callback_data=str(p['_id'])))
    keyboard.append([telegram.InlineKeyboardButton('back', callback_data='/back')])
    reply_markup = telegram.InlineKeyboardMarkup(keyboard)
    bot.edit_message_text(
        text='your pr:',
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        reply_markup=reply_markup
    )
    return MY


def error(bot, update, user_data):
    update.message.reply_text('wtf')
    return REQ


def done(bot, update, user_data):
    if 'choice' in user_data:
        del user_data['choice']
    update.message.reply_text(str(user_data))
    user_data.clear()
    return ConversationHandler.END


def _error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


commands = [
    CommandHandler('start', start, pass_user_data=True),
    CommandHandler('push', push_model_get, pass_user_data=True),
    CommandHandler('location', location_get, pass_user_data=True),
    CommandHandler('contact', contact_get, pass_user_data=True),
    CommandHandler('my', my_pr, pass_user_data=True),
]

index_of_todo = 0
def prepone(todo_list):
    import random
    global index_of_todo
    todo = todo_list[index_of_todo]
    index_of_todo += 1
    def deco(f):
        def decee(bot, update, user_data):
            if random.random() < .1:
                user_data['redirect'] = f
                return todo(bot, update, user_data)
            return f(bot, update, user_data)
        return decee
    return deco


def answer(bot, update, user_data):
    return user_data['answer'](bot, update, user_data)


def ask_motivation(bot, update, user_data):
    user_id = update.message.chat_id
    user = users.find_one({'_id': user_id})
    if 'motivation' in user:
        return user_data['redirect'](bot, update, user_data)
    user_data['answer'] = answer_motivation
    keyboard = [[
        telegram.InlineKeyboardButton('local', callback_data=0),
        telegram.InlineKeyboardButton('town', callback_data=1),
        telegram.InlineKeyboardButton('city', callback_data=2),
    ]]
    reply_markup = telegram.InlineKeyboardMarkup(keyboard)
    update.message.reply_text(
        'how far would you go for buying cheaper pr:',
        reply_markup=reply_markup
    )
    return PRETTY_RANDOM_QUESTIONS


def answer_motivation(bot, update, user_data):
    query = update.callback_query
    action = query.data
    user_id = query.message.chat_id
    user = users.find_one({'_id': user_id})
    user['motivation'] = action
    bot.edit_message_text(
        text='your answer was: ' + action,
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
    )
    return user_data['redirect'](bot, update, user_data)


def main():
    # Create the Updater and pass it your bot's token.
    updater = Updater('503798742:AAHzfg7uqG8z6RU1p0C3ktRf0uPO2FNMb4Q')

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start, pass_user_data=True)],

        states={
            REQ: [
                *commands,
                MessageHandler(Filters.text, req, pass_user_data=True),
                CallbackQueryHandler(add_listener, pass_user_data=True),
            ],
            PUSH_MODEL: [
                *commands,
                MessageHandler(Filters.text, req, pass_user_data=True),
                CallbackQueryHandler(push_model_post, pass_user_data=True),
            ],
            PUSH_PRICE: [
                *commands,
                MessageHandler(Filters.text, push_price, pass_user_data=True)
            ],
            CONTACT: [
                *commands,
                MessageHandler(Filters.contact | Filters.text, contact_push, pass_user_data=True)
            ],
            LOCATION: [
                *commands,
                MessageHandler(Filters.location | Filters.text, location_post, pass_user_data=True),
                CallbackQueryHandler(location_post, pass_user_data=True),
            ],
            MY: [
                *commands,
                CallbackQueryHandler(product_get, pass_user_data=True),
            ],
            PRODUCT: [
                *commands,
                CallbackQueryHandler(product_post, pass_user_data=True),
            ],
            PRETTY_RANDOM_QUESTIONS: [
                *commands,
                CallbackQueryHandler(answer, pass_user_data=True)
            ],
        },

        fallbacks=[RegexHandler('^Done$', done, pass_user_data=True)]
    )

    dp.add_handler(conv_handler)

    # log all errors
    dp.add_error_handler(_error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()