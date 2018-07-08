# Бот приемной кампании

Бот, который показывает статистику приема на кафедру КТ в 2018 году. Написан на Python 3, использует MongoDB и BeautifulSoup.

## Деплой

1. Создай бота у [@BotFather](https://t.me/BotFather) и запомни токен

2. Узнай свой ID в Telegram (например, у `@get_id_bot`)

3. Склонируй себе репозиторий: `git clone https://github.com/nsychev/abit-bot.git`

4. Создай файл `bot/config.py`, указав там всё необходимое для бота:

```python
TOKEN = "123456789:QWERTYUIOPasdfghjkl123456789ZXCVBNM"
ADMIN_ID = 97631681

STATS_URL_BUDGET = "http://abit.ifmo.ru/bachelor/statistics/applications/11000181/"
STATS_URL_PAID = "http://abit.ifmo.ru/bachelor/statistics/applications/12000181/"
RANKING_URL = "http://abit.ifmo.ru/bachelor/rating_rank/all/181/"
```

5. Установи [Docker](https://docs.docker.com/install/) и [docker-compose](https://docs.docker.com/compose/install/)

6. Запусти бота: 

```bash
docker-compose up --build -d
```

7. Чтобы получить обновляемую статистику, напиши `/stats` в чат

8. В директории `static/` генерируется файл `main.html` с подробной статистикой в форме таблицы

----

Автор — [Никита Сычев](https://github.com/nsychev), по всем вопросам пиши мне [в телеграм](https://t.me/nsychev)

Код распространяется по [лицензии MIT](LICENSE)

