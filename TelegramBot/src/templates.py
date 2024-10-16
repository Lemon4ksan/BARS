from telegram import InlineKeyboardButton
from collections.abc import Sequence

USER_DICT: dict = {
    'sessionid': None,
    'pupilid': None,
    'current_operation': None,
    'total_marks': None,
    'schedule_week': None,
    'homework_week': None,
    'diary_week': None
}

WELCOME_TEXT: str = r"""Этот бот позволит вам пользоваться сервисами БАРС альтернативным способом.

*Настройка*
/set\_sessionid - Установить ID сессии

*Уроки*
/get\_diary - Дневник
/get\_homework - Домашнее задание
/get\_schedule\_day - Расписание на день

*Успеваемость*
/get\_summary\_marks - Сводные оценки
/get\_total\_marks - Итоговые оценки
/get\_attendance\_data - Данные о посещаемости
/get\_progress\_data - Данные об успеваемости

*Школа*
/get\_school\_info - Информация об учебном заведении
/get\_class\_info - Информация о классе

*События*
/get\_birthdays - Текущие Дни Рождений
/get\_events - Текущие праздники"""

WHAT_IS_SID: str = """sessionid - это идентификатор вашей сессии. Благодаря нему можно костыльно получить данные вашего аккаунта вне сайта.

Чтобы получить данное значение:
1. Задите на сайт с ПК.
2. Откройте панель разработчика (Ctrl+Shift+I).
3. Перейдите во вкладку Приложение (Application).
4. Откройте Хранилище > Файлы cookie.
5. Скопируйте значение ключа sessionid.

Чтобы сессия не заканчивалась, измените её дату истекания (Expires/Max-Age) на [ГОД]-04-18T13:10:00.000Z заменив [ГОД] на следующий."""

SID_BUTTON: Sequence[Sequence['InlineKeyboardButton']] = [[InlineKeyboardButton(text='Что такое sessionid?', callback_data='about_sid')]]

DIARY_LESSON_TEMPLATE: str = """\n*{discipline}*{theme}{mark_info}{comment}{remarks}{attendance}\n"""

HOMEWORK_LESSON_TEMPLATE: str = """\n*{discipline}*\n{homework} {time_to_complete}{materials}\n"""

SCHEDULE_DAY_TEMPLATE: str = """\n*{discipline}*\n{teacher}\n{office}\n{start}-{end}\n"""

SCHOOL_INFO_TEMPLATE: str = """Адрес: {}
Номер телефона: {}
Сайт школы: {}
Кол-во рабочих: {}
Кол-во учашихся: {}
Почта: {}"""

CLASS_INFO_TEMPLATE: str = """*{}{}*
Классный руководитель: {}
Направление: {}
Ученики: {}\n{}"""

ATTENDANCE_TEMPLATE: str = """Всего: {}
Посещено: {}
Пропущено: {}
По уважительной причине: {}
По неуважительной причине: {}
По болезни: {}"""

DIARY_BUTTONS: Sequence[Sequence['InlineKeyboardButton']] = [
    [InlineKeyboardButton(text='Предыдущий день', callback_data='diary_previous_day'),
     InlineKeyboardButton(text='Следующий день', callback_data='diary_next_day')],
]

HOMEWORK_BUTTONS: Sequence[Sequence['InlineKeyboardButton']] = [
    [InlineKeyboardButton(text='Предыдущий день', callback_data='homework_previous_day'),
     InlineKeyboardButton(text='Следующий день', callback_data='homework_next_day')],
]

SCHEDULE_DAY_BUTTONS: Sequence[Sequence['InlineKeyboardButton']] = [
    [InlineKeyboardButton(text='Предыдущий день', callback_data='schedule_previous_day'),
     InlineKeyboardButton(text='Следующий день', callback_data='schedule_next_day')],
]

TOTAL_MARKS_BUTTONS: Sequence['InlineKeyboardButton'] = [
    InlineKeyboardButton(text='1 Четверть', callback_data='total_marks_subperiod1'),
    InlineKeyboardButton(text='2 Четверть', callback_data='total_marks_subperiod2'),
    InlineKeyboardButton(text='3 Четверть', callback_data='total_marks_subperiod3'),
    InlineKeyboardButton(text='4 Четверть', callback_data='total_marks_subperiod4')
]
