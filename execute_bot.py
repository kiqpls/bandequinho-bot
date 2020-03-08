from bot import BandecoBot

import locale
import calendar
from datetime import datetime

locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')


def get_weekday(ts):
    weekdays_names = dict(zip(range(7), list(calendar.day_name)))
    weekday_name = weekdays_names[ts.weekday()]
    return weekday_name.title()


def get_mealtime(ts):
    if ts.hour <= 13:
        return 'Almoço'
    else:
        return 'Jantar'


def run():
    ts = datetime.now()

    weekday = get_weekday(ts)
    meal_time = get_mealtime(ts)

    bot = BandecoBot(
        meal_time=meal_time,
        weekday=weekday,
        date=ts.date()
    )

    bot.post_twitter_thread()

    return


if __name__ == '__main__':
    run()
