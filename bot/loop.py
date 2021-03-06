#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from telegram import Bot
from config import *
from time import sleep
from pymongo import MongoClient
import fetcher
import levels
import message
import traceback
import sys
from jinja2 import Template

client = MongoClient("db", 27017)
db = client.db
bot = Bot(TOKEN)
template = Template(open("template.html", "r", encoding="utf-8").read())

CATEGORIES = {
    "без вступительных испытаний": "olymp",
    "на бюджетное место в пределах особой квоты": "quota",
    "по общему конкурсу": "exams",
    "на контрактной основе": "paid"
}


def safe_int(value):
    return int(value) if value is not None else 0


def cut_options(value, options):
    for option in options:
        if value.endswith(option):
            return value[:-len(option)-1], option
    raise KeyError("Pattern did not match: " + value)


def parse_olymp(text):
    if text is None or text == "":
        return None

    olymp, status = cut_options(
        text.strip(),
        ["победитель", "призер"]
    )
    winner = status == "победитель"

    level = levels.get(olymp)

    try:
        olymp, subject = cut_options(
            olymp,
            ["математика", "информатика", "информационные технологии"]
        )
    except KeyError:
        subject = ""

    if level == 4:
        print("Not found:", olymp, "|", subject, "|", winner, "|", level, file=sys.stderr, flush=True)

    return {
        "name": olymp,
        "subject": subject,
        "winner": winner,
        "level": level
    }


def load_lists():
    global db

    ranking = fetcher.get(RANKING_URL)[2:]  # cut header off

    for line in ranking:
        if len(line) != 16:
            raise Exception("Bad line from abit.ifmo.ru: " + str(line))

        category, uid, order, full_name, exam_type, math, \
        cs, rus, sum_ach, sum_exams, ach, has_orig, \
        agreed, adv, olymp, status = line

        db.abits.find_one_and_update(
            {
                "full_name": full_name, 
                "category": CATEGORIES.get(category, category)
            },
            {"$set": {
                "full_name": full_name,
                "category": CATEGORIES.get(category, category),
                "exam_type": exam_type,
                "results": {"math": safe_int(math), "cs": safe_int(cs), "rus": safe_int(rus), "ach": safe_int(ach)},
                "has_orig": "Да" in has_orig,
                "agreed": "Да" in agreed,
                "adv": "Да" in adv,
                "olymp": parse_olymp(olymp),
                "status": status,
                "updated": True
            }},
            upsert=True
        )


def update_messages():
    global db

    message_text = message.get(db)

    for task in db.tasks.find():
        bot.edit_message_text(
            chat_id=task["chat_id"],
            message_id=task["message_id"],
            text=message_text,
            parse_mode="Markdown",
            disable_web_page_preview=True)


def generate_page():
    global db

    abits = []

    for abit in db.abits.find({}):
        if abit["results"].get("sum") is None:
            abit["results"]["sum"] = abit["results"]["math"] + abit["results"]["cs"] + \
                                     abit["results"]["rus"] + abit["results"]["ach"]

        abit["has_orig_word"] = "Да" if abit["has_orig"] else "Нет"
        abit["agreed_word"] = "Да" if abit["agreed"] else "Нет"
        abit["exam_type"] = abit["exam_type"] or ""

        if abit["category"] == "quota":
            abit["priority"] = 40
            abit["entr_type"] = "ОК"
        elif abit["category"] == "paid":
            abit["priority"] = 60
            abit["entr_type"] = "К"
        elif abit["category"] == "exams":
            abit["priority"] = 50
            abit["entr_type"] = "Б"
        else: # abit["category"] == "olymp"
            abit["priority"] = abit["olymp"]["level"] * 10
            abit["entr_type"] = "БВИ"
            if not abit["olymp"]["winner"]:
                abit["priority"] += 1

            del abit["results"]["math"]
            del abit["results"]["rus"]
            del abit["results"]["cs"]

            abit["olymp"]["level_roman"] = {0: "×", 1: "I", 2: "II", 3: "III"}[abit["olymp"]["level"]]

            abit["olymp_style"] = "olymp-{}-{}".format(
                abit["olymp"]["level"],
                "win" if abit["olymp"]["winner"] else "prz"
            )

            abit["olymp"]["status"] = "победитель" if abit["olymp"]["winner"] else "призер"
            if abit["olymp"]["level"] <= 1:
                medal = "gold"
            elif abit["olymp"]["level"] == 2:
                medal = "silver"
            else:
                medal = None
            if medal:
                abit["ticket_style"] = medal + " medal"

        if abit["category"] in ["quota", "exams"] and abit["exam_type"] == "ЕГЭ":
            plain_sum = abit["results"]["math"] + abit["results"]["cs"] + abit["results"]["rus"]
            if plain_sum >= 290:
                abit["ticket_style"] = "gold medal"
            elif plain_sum >= 280:
                abit["ticket_style"] = "silver medal"
            elif plain_sum >= 270:
                abit["ticket_style"] = "bronze medal"

        abits.append(abit)

    abits.sort(key=lambda abit: (abit["priority"], -abit["results"]["sum"], abit["full_name"]))

    id_budget = 1
    id_quota = 1
    id_paid = 1

    id_budget_agr = 1
    id_quota_agr = 1

    for abit in abits:
        if abit["category"] == "quota":
            if id_quota <= LIMIT_QUOTA:
                abit["entr_style"] = "entr-ok"
            elif id_quota_agr <= LIMIT_QUOTA:
                abit["entr_style"] = "entr-maybe"
            else:
                abit["entr_style"] = "entr-no"

            abit["id"] = id_quota
            id_quota += 1

            if abit["agreed"] and abit["has_orig"]:
                id_quota_agr += 1
        elif abit["category"] == "paid":
            abit["entr_style"] = "entr-ok"
            abit["id"] = id_paid
            id_paid += 1
        else:
            if abit["category"] == "olymp" or \
               id_budget <= LIMIT_BUDGET - min(LIMIT_QUOTA, id_quota - 1):
                abit["entr_style"] = "entr-ok"
            elif id_budget_agr <= LIMIT_BUDGET - min(LIMIT_QUOTA, id_quota_agr - 1):
                abit["entr_style"] = "entr-maybe"
            else:
                abit["entr_style"] = "entr-no"

            abit["id"] = id_budget
            id_budget += 1

            if abit["agreed"] and abit["has_orig"]:
                id_budget_agr += 1

        if abit["agreed"] and abit["has_orig"]:
            abit["entr_style"] += " entr-has-orig"
    with open("../static/main.html", "w") as f:
        f.write(template.render(abits=abits))


def main():
    global db

    while True:     
        try:
            db.abits.update_many({}, {"$set": {"updated": False}})
            load_lists()
            db.abits.delete_many({"updated": False})

            update_messages()
            generate_page()
        except:
            traceback.print_exc()
            sys.stderr.flush()
        
        sleep(120)


if __name__ == "__main__":
    main()
