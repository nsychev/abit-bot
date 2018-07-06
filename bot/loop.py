#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from telegram import Bot
from config import *
from time import sleep
from pymongo import MongoClient
import fetcher
import levels
import message


def safe_int(value):
    return int(value) if value is not None else 0


def parse_olymp(text):
    if text is None or text == "":
        return None

    *olymp, status = text.split()
    olymp = " ".join(olymp)
    winner = status == "победитель"
    level = levels.get(olymp)

    last_word = olymp.split()[-1]
    if last_word in ["математика", "информатика"]:
        subject = last_word
        olymp = " ".join(olymp.split()[:-1])
    else:
        subject = ""
    
    return {
        "name": olymp,
        "subject": subject,
        "winner": winner,
        "level": level
    }


def main():
    bot = Bot(TOKEN)
    client = MongoClient("db", 27017)
    db = client.db

    while True:     
        try:
            ranking = fetcher.get(RANKING_URL)[2:] # cut header off

            for line in ranking:
                if len(line) != 16:
                    raise Exception("Bad line from abit.ifmo.ru: " + str(line))

                category, uid, order, full_name, exam_type, math, \
                cs, rus, sum_ach, sum_exams, ach, has_orig, \
                agreed, adv, olymp, status = line
                
                db.abits.find_one_and_update(
                    {"full_name": full_name},
                    {"$set": {
                        "full_name": full_name,
                        "category": CATEGORIES.get(category, category),
                        "exam_type": exam_type,
                        "results": {"math": safe_int(math), "cs": safe_int(cs), "rus": safe_int(rus), "ach": safe_int(ach)},
                        "has_orig": "Да" in has_orig,
                        "agreed": "Да" in agreed,
                        "adv": "Да" in adv,
                        "olymp": parse_olymp(olymp),
                        "status": status
                    }},
                    upsert=True
                )

            message_text = message.get(db)
            
            for task in db.tasks.find():
                bot.edit_message_text(
                    chat_id=task.chat_id,
                    message_id=task.message_id,
                    text=message_text, 
                    parse_mode="Markdown",
                    disable_web_page_preview=True)
        except Exception as e:
            raise
        
        sleep(120)


if __name__ == "__main__":
    main()
