from datetime import datetime, timedelta


def ending(num, end1, end2, end5):
    if (num % 100) in range(11, 15):
        return end5
    if num % 10 == 1:
        return end1
    if 2 <= num % 10 <= 4:
        return end2
    return end5


def get(db):
    abits = db.abits.count_documents({})
    quota = db.abits.count_documents({"category": "quota"})
    olymp = db.abits.count_documents({"category": "olymp"})

    win0 = db.abits.count_documents({"olymp.level": 0, "olymp.winner": True})
    prz0 = db.abits.count_documents({"olymp.level": 0, "olymp.winner": False})
    win1 = db.abits.count_documents({"olymp.level": 1, "olymp.winner": True})
    prz1 = db.abits.count_documents({"olymp.level": 1, "olymp.winner": False})
    win2 = db.abits.count_documents({"olymp.level": 2})

    time = (datetime.now() + timedelta(hours=3)).strftime("%H:%M")

    return f'''Подано *{olymp}* заявлени{ending(olymp, "е", "я", "й")} БВИ

[FAQ для абитуриента](https://ctd.page.link/faq)

Всерос и etc: *{win0}* победител{ending(win0, "ь", "я", "ей")} и *{prz0}* \
призер{ending(prz0, "", "а", "ов")}
I уровень: *{win1}* победител{ending(win1, "ь", "я", "ей")} и *{prz1}* \
призер{ending(prz1, "", "а", "ов")}
II уровень: *{win2}* победител{ending(win2, "ь", "я", "ей")}

Всего [{abits} абитуриент{ending(abits, "", "а", "ов")}]\
(https://ctd.page.link/enroll2018), в том числе *{quota}*\
 — на места в пределах особой квоты
 
_Обновлено в {time}_ [ботом](https://github.com/nsychev/abit-bot) _от_ @nsychev'''
