import json
from collections.abc import Sequence
from datetime import datetime, timedelta
from typing import Optional

from telegram import Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes

import BARS
import templates
from BARS import BClientAsync
from utils.general import get_user_from_db, update_db, escape_illegal_chars
from utils.commands_utils import proccess_diary, proccess_homework, proccess_schedule


# TODO: Добавить опцию для учёта субботы


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Инициализация пользователя в датабазе. Вывод доступных команд."""

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=templates.WELCOME_TEXT,
        parse_mode='Markdown'
    )
    try:
        with open('../db.json', 'r') as f:
            contents = dict(json.load(f))
    except FileNotFoundError:
        with open('../db.json', 'w') as f:
            json.dump({}, f)
        contents = {}

    user = str(update.message.from_user.id)
    if user not in contents:
        contents[str(update.message.from_user.id)] = templates.USER_DICT
    update_db(contents)


async def set_sessionid(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда /set_sessionid. Устанавливает sessionid. Записывает в датабазу."""

    await update.message.reply_text('Введите sessionid')
    user: dict = get_user_from_db(update)
    user['current_operation'] = 'sessionid'
    update_db(user, update)


async def get_diary(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        *,
        date: Optional[datetime] = None,
        delta=timedelta(0)
) -> None:
    """Комманда /get_diary. Выводит неделю из дневника.

    ``date`` указывется для указания точки смещения. Если значение пустое, используется сегодняшний день.
    ``delta`` указывается для смещения времени при достижении края недели.

    Добавляет в поле пользователя ``{'diary_week': {'current_weekday': 0-4, i: [{date: str, discipline: str, theme: str, mark_info: str, comment: str remarks: str},...],... }}``
    
    где ``i`` - индекс дня (0-4, строка). Суббота исключается.

    Использует Inline клавиатуру."""

    if date is None:
        date = datetime.now().date()

    user: dict = get_user_from_db(update)
    date += delta
    if date.weekday() in [5, 6]:  # Перейти на следующую неделю, если выходной
        date += timedelta(7 - date.weekday())
    result_dict: dict = {'current_weekday': date.weekday()}

    async with BClientAsync(user['sessionid']) as client:
        diary_days: Sequence['BARS.DiaryDay'] = await client.get_diary(date)

    send_text: str = proccess_diary(result_dict, diary_days, date)
    user['diary_week'] = result_dict
    update_db(user, update)

    reply_markup = InlineKeyboardMarkup([*templates.DIARY_BUTTONS])

    try:
        await update.message.reply_text(send_text, parse_mode='Markdown', reply_markup=reply_markup)
    except AttributeError:  # При переходе на другую неделю сообщение None
        return


async def get_homework(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        *,
        date: Optional[datetime] = None,
        delta=timedelta(0)
) -> None:
    """Комманда /get_homework. Выводит домашнее задание.

    ``date`` указывется для указания точки смещения. Если значение пустое, используется сегодняшний день.
    ``delta`` указывается для смещения времени при достижении края недели.

     Записывает в датабазу: ``{'homework_week': {'current_weekday': 0-4, i: [Последовательность д/з]}}``,
     где ``i`` - индекс дня (0-4, строка). Суббота исключается.

     Использует Inline клавиатуру."""

    if date is None:
        date = datetime.now().date()

    user: dict = get_user_from_db(update)
    date += delta
    if date.weekday() in [5, 6]:  # Перейти на следующую неделю, если выходной
        date += timedelta(7 - date.weekday())
    result_dict: dict = {'current_weekday': date.weekday()}

    async with BClientAsync(user['sessionid']) as client:
        homework: Sequence['BARS.HomeworkDay'] = await client.get_homework(date)

    send_text: str = proccess_homework(result_dict, homework, client.base_url, date)
    user['homework_week'] = result_dict
    update_db(user, update)

    reply_markup = InlineKeyboardMarkup([*templates.HOMEWORK_BUTTONS])

    try:
        await update.message.reply_text(send_text, parse_mode='Markdown', reply_markup=reply_markup)
    except AttributeError:  # При переходе на другую неделю сообщение None
        return


async def get_schedule_day(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        date: Optional[datetime] = None,
        delta=timedelta(0)
) -> None:
    """Команда /get_schedule_day. Расписание на день/неделю. Записывает в датабазу. Использует Inline клавиатуру.

    ``date`` указывется для указания точки смещения. Если значение пустое, используется сегодняшний день.
    ``delta`` указывается для смещения времени при достижении края недели.
    """

    if date is None:
        date = datetime.now().date()

    user: dict = get_user_from_db(update)
    date += delta
    if date.weekday() in [5, 6]:
        date += timedelta(7 - date.weekday())
    result_dict: dict = {'current_weekday': date.weekday()}

    async with BClientAsync(user['sessionid']) as client:
        schedule_week: Sequence['BARS.ScheduleDay'] = await client.get_week_schedule(date)

    send_text: str = proccess_schedule(result_dict, schedule_week, date)
    user['schedule_week'] = result_dict
    update_db(user, update)

    reply_markup = InlineKeyboardMarkup([*templates.SCHEDULE_DAY_BUTTONS])

    try:
        await update.message.reply_text(send_text, parse_mode='Markdown', reply_markup=reply_markup)
    except AttributeError:  # При переходе на другую неделю сообщение None
        return


async def get_summary_marks(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда /get_simmary_marks. Сводные оценки."""

    user: dict = get_user_from_db(update)
    async with BClientAsync(user['sessionid']) as client:
        summary_marks: 'BARS.SummaryMarks' = await client.get_summary_marks(datetime.now().date())

    send_text: str = ''
    for discipline in summary_marks.disciplines:
        marks = [str(marks.mark) for marks in discipline.marks]
        send_text += f"\n*{discipline.discipline}*: {discipline.average_mark}\n{' '.join(marks)}"

    await update.message.reply_text(send_text, parse_mode='Markdown')


async def get_total_marks(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда /get_total_marks. Итоговые оценки. Записывает в датабазу. Использует Inline клавиатуру.
    Использует обработчик сообщений."""

    user: dict = get_user_from_db(update)
    total_marks_dict: dict = {}

    async with BClientAsync(user['sessionid']) as client:
        total_marks: 'BARS.TotalMarks' = await client.get_total_marks()

    period: 'BARS.Subperiod'  # Четверть
    discipline_mark: 'BARS.TotalMarksDiscipline'  # Сборник оценок по предмету
    i: int  # Индекс четверти
    # Конвертация запутанная, т.к. API был создан только для работы с таблицей на самом сайте.

    for period, discipline_mark, i in zip(total_marks.subperiods, total_marks.disciplines, range(4)):
        text: str = '\n' + period.name + '\n'

        if discipline_mark.period_marks:
            text += f"{discipline_mark.discipline}: {discipline_mark.period_marks[i]}\n"
        else:
            text += 'Оценок нет\n'
        total_marks_dict[i] = text

    user['total_marks'] = total_marks_dict
    update_db(user, update)

    reply_markup = InlineKeyboardMarkup([
        [templates.TOTAL_MARKS_BUTTONS[0], templates.TOTAL_MARKS_BUTTONS[1]],
        [templates.TOTAL_MARKS_BUTTONS[2], templates.TOTAL_MARKS_BUTTONS[3]]
    ])
    await update.message.reply_text('Выберите четверть', reply_markup=reply_markup)


async def get_attendance_data(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда /get_attendance_data. Данные о посещаемости. Использует обработчик сообщений."""

    await update.message.reply_text('Введите название предмета или `Все` для общей статистики')
    user: dict = get_user_from_db(update)
    user['current_operation'] = 'attendancedata'
    update_db(user, update)


async def get_progress_data(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда /get_progress_data. Данные об успеваемости. Использует обработчик сообщений."""

    await update.message.reply_text('Введите название предмета или `Все` для общей статистики')
    user: dict = get_user_from_db(update)
    user['current_operation'] = 'progressdata'
    update_db(user, update)


async def get_school_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда /get_school_info. Информация о школе."""

    user: dict = get_user_from_db(update)
    async with BClientAsync(user['sessionid']) as client:
        school_info: 'BARS.SchoolInfo' = await client.get_school_info()

    send_text: str = f"*{escape_illegal_chars(school_info.name)}*\n\n"
    send_text += templates.SCHOOL_INFO_TEMPLATE.format(
        escape_illegal_chars(school_info.address),
        escape_illegal_chars(school_info.phone),
        escape_illegal_chars(school_info.site_url),
        str(school_info.count_employees),
        str(school_info.count_pupils),
        escape_illegal_chars(school_info.email)
    )
    await update.message.reply_text(send_text, parse_mode='Markdown')


async def get_class_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команада /get_class_info. Информация о классе."""

    user: dict = get_user_from_db(update)

    async with BClientAsync(user['sessionid']) as client:
        class_info: 'BARS.ClassInfo' = await client.get_class_info()

    pupils: Sequence[str] = [pupil.fullname for pupil in class_info.pupils]
    send_text: str = templates.CLASS_INFO_TEMPLATE.format(
        class_info.study_level,
        class_info.letter,
        class_info.form_master,
        class_info.specialization,
        len(pupils),
        "\n".join(pupils)
    )
    await update.message.reply_text(send_text, parse_mode='Markdown')


async def get_birthdays(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда /get_birthdays. Текущие дни рождения."""

    user: dict = get_user_from_db(update)

    async with BClientAsync(user['sessionid']) as client:
        birthdays: Sequence['BARS.Birthday'] = await client.get_birthdays()

    send_text: str = "Дни Рождения:\n" if birthdays else "Дни Рождения отсутствуют"

    for birthday in birthdays:
        send_text += f"*{birthday.date}*\n{escape_illegal_chars(birthday.short_name)}\n\n"

    await update.message.reply_text(send_text, parse_mode='Markdown')


async def get_events(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда /get_events. Текущие события/праздники."""

    user: dict = get_user_from_db(update)

    async with BClientAsync(user['sessionid']) as client:
        events: Sequence['BARS.Event'] = await client.get_events()

    send_text: str = "Текущие мероприятия:\n" if events else "Мероприятия отсутствуют"

    for event in events:
        send_text += f"*{escape_illegal_chars(event.date_str)}*\n{escape_illegal_chars(event.theme)}\n\n"

    await update.message.reply_text(send_text, parse_mode='Markdown')
