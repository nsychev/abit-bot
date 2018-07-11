#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from telegram.ext import Updater, CommandHandler, Filters
import logging
from config import *
import message
from pymongo import MongoClient
from datetime import datetime, timedelta


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)
client = MongoClient("db", 27017)
db = client.db


def only_pm(func):
    def inner(bot, update, *args, **kwargs):
        if not update.message:
            return
        if update.message.chat.id != update.message.from_user.id:
            return
        return func(bot, update, *args, **kwargs)
    return inner


@only_pm
def start(bot, update, args):
    if len(args) == 1 and args[0] == "bet":
        update.message.reply_text("Сделай ставку на число БВИ: /bet [число]\nВсе ставки — /bets\n\nСтавку можно поставить и поменять до 13 июля 12:00 MSK", parse_mode="Markdown")
        return
    update.message.reply_text(
        '''Привет! Я бот для абитуриентов КТ 2018
        
Статистика приема в чате @abit_ct и <a href="https://abit.nsychev.ru">в таблице</a>
/bet — ставки на число БВИ

Сделал @nsychev, <a href="https://github.com/nsychev/abit-bot">исходники на гитхабе</a>''',
        parse_mode="HTML",
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
    

@only_pm
def bet(bot, update, args):
    if datetime.now() >= datetime(2018, 7, 13, 9, 0, 0): # UTC
        update.message.reply_text("\u274c Ставки сделаны, ставок больше нет")
        return

    if len(args) != 1:
        update.message.reply_text("Сделать ставку на число БВИ: /bet [число]\nСтавку можно менять до 13 июля 12:00", parse_mode="Markdown")
        return
    try:
        num = int(args[0])
    except:
        update.message.reply_text("Твоя ставка не похожа на число :( Напиши /bet [число] (без квадратных скобок)", parse_mode="Markdown")
        return

    user = update.message.from_user
    uid = user.id
    display_name = ""
    if user.username:
        display_name = "@" + user.username
    else:
        display_name = user.first_name
        if user.last_name:
            display_name += " " + user.last_name

    db.bets.find_one_and_update(
        {"id": uid}, 
        {"$set": {
            "id": uid,
            "display_name": display_name,
            "bet": num,
            "timestamp": datetime.now() + timedelta(hours=3)
        }},
        upsert=True
    )

    update.message.reply_text("Ставка сделана! Если хочешь, можешь поменять её, просто повторив команду с новым числом\n\nВсе ставки — /bets")
    

@only_pm
def bets(bot, update):
    message = "<b>Список сделанных ставок</b>\n\n"
    
    for bet in db.bets.find({}, sort=[("bet", 1), ("timestamp", 1)]):
        message += f"{bet['display_name']} — {bet['bet']} [{bet['timestamp'].strftime('%d.%m %H:%M')}]\n"
    
    update.message.reply_text(message, parse_mode="HTML")


def error(bot, update, info):
    logger.warning('Update "%s" caused error "%s"', update, info)


def main():
    updater = Updater(TOKEN)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start, pass_args=True))
    dp.add_handler(CommandHandler("stats", stats))
    dp.add_handler(CommandHandler("bet", bet, pass_args=True))
    dp.add_handler(CommandHandler("bets", bets))

    dp.add_error_handler(error)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()

