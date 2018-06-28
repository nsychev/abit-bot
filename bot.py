#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from telegram.ext import Updater, CommandHandler, Filters
import logging
from config import *
from util import generate_message

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


def only_pm(func):
    def inner(bot, update):
        if not update.message:
            return
        if update.message.chat.id != update.message.from_user.id:
            return
        return func(bot, update)
    return inner


@only_pm
def start(bot, update):
    update.message.reply_text("Привет! Я показываю статистику в чате абитуры, больше я ничего пока не умею (но скоро научусь) :(")
    

def send_updatable(bot, update):
    if not update.message or update.message.from_user.id != ADMIN_ID:
        return
    
    message_text = generate_message()
    message = bot.send_message(
        chat_id=update.message.chat.id, 
        text=message_text, 
        parse_mode="Markdown",
        disable_web_page_preview=True)
    
    with open("messages.txt", "a") as f:
        print(
            message.chat.id, 
            message.message_id, 
            file=f, 
            sep=":")

    
def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    updater = Updater(TOKEN)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("send", send_updatable))

    dp.add_error_handler(error)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()

