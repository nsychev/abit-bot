#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from telegram.ext import Updater, CommandHandler, Filters
import logging
from config import *
import message
from pymongo import MongoClient


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)
client = MongoClient("db", 27017)
db = client.db


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
    global db
    update.message.reply_text(
        message.get(db),
        parse_mode="Markdown",
        disable_web_page_preview=True)


def stats(bot, update):
    if update.message.from_user.id != ADMIN_ID:
        return
    global db
    sent_message = bot.send_message(
        chat_id=update.message.chat.id,
        text=message.get(db),
        parse_mode="Markdown",
        disable_web_page_preview=True
    )
    db.tasks.insert_one({
        "chat_id": sent_message.chat.id,
        "message_id": sent_message.message_id
    })
    

def error(bot, update, info):
    logger.warning('Update "%s" caused error "%s"', update, info)


def main():
    updater = Updater(TOKEN)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("stats", stats))

    dp.add_error_handler(error)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()

