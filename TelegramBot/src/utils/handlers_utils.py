from datetime import datetime, timedelta

from telegram import Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes

import BARS
from BARS import BClientAsync

from ..exceptions import TelegramBotError
from ..general import update_db, get_user_from_db, get_school_start_year
from ..commands import get_diary, get_homework, get_schedule_day
from ..templates import (
    ATTENDANCE_TEMPLATE,
    DIARY_BUTTONS, DIARY_LESSON_TEMPLATE,
    HOMEWORK_BUTTONS, HOMEWORK_LESSON_TEMPLATE,
    SCHEDULE_DAY_BUTTONS, SCHEDULE_DAY_TEMPLATE
)


async def process_sessionid(update: Update, user: dict) -> None:
    """Обработать ввод sessionid."""

    if update.message is None:
        raise TelegramBotError()
    
    sessionid = update.message.text

    if sessionid is None:
        raise TelegramBotError()

    async with BClientAsync(sessionid) as client:
        pupil_info: BARS.PupilInfo = await client.get_pupil_info()
        acount_info: BARS.AccountInfo = await client.get_account_info()

    name: str = pupil_info.user_fullname.split()[1]
    await update.message.reply_text(f'Привет, {name}!')

    user['sessionid'] = update.message.text
    user['pupilid'] = acount_info.pupilid


async def process_attendancedata(update: Update, user: dict) -> None:
    """Обработать ввод данных для посещаемости."""

    if update.message is None:
        raise TelegramBotError()
    elif update.message.text is None:
        raise TelegramBotError()

    async with BClientAsync(user['sessionid']) as client:
        account: BARS.AccountInfo = await client.get_account_info()
        if update.message.text.lower() == 'все':
            subjectid: int = 0
            send_text: str = "*Общие данные*\n"
        else:
            for discipline in account.disciplines:
                if update.message.text.lower() in discipline.name.lower():
                    subjectid: int = discipline.id
                    send_text: str = f"*{discipline.name}*\n"
                    break
            else:
                await update.message.reply_text(f'❌ Недоступный предмет "{update.message.text}"')
                return

        attendance_data: BARS.AttendaceData = await client.get_attendace_data(
            user['pupilid'],
            f"{get_school_start_year()}-09-01",
            f"{get_school_start_year() + 1}-08-31",
            subjectid
        )

    send_text += ATTENDANCE_TEMPLATE.format(
        attendance_data.total,
        attendance_data.present,
        attendance_data.absent,
        attendance_data.absent_good,
        attendance_data.absent_bad,
        attendance_data.ill
    )
    send_text += f'\n\nВы были на {int(round(attendance_data.present / attendance_data.total, 2) * 100)}% уроков!'

    await update.message.reply_text(send_text, parse_mode='Markdown')


async def process_progressdata(update: Update, user: dict) -> None:
    """Обработать ввод данных для успеваемости."""

    if update.message is None:
        raise TelegramBotError()
    elif update.message.text is None:
        raise TelegramBotError()

    async with BClientAsync(user['sessionid']) as client:
        account: BARS.AccountInfo = await client.get_account_info()
        if update.message.text.lower() == 'все':
            subjectid: int = 0
            send_text: str = "*Общие данные*\n"
        else:
            for discipline in account.disciplines:
                if update.message.text.lower() in discipline.name.lower():
                    subjectid: int = discipline.id
                    send_text: str = f"*{discipline.name}*\n"
                    break
            else:
                await update.message.reply_text(f'❌ Недоступный предмет "{update.message.text}"')
                return

        progress_data: BARS.ProgressData = await client.get_progress_data(
            user['pupilid'],
            f"{get_school_start_year()}-09-01",
            f"{get_school_start_year() + 1}-08-31",
            subjectid
        )

    for date, mark in zip(progress_data.dates, progress_data.series[0].data):
        send_text += f"*{date}*: {round(mark, 2)}\n"

    await update.message.reply_text(send_text, parse_mode='Markdown')


async def process_diary(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        user: dict,
        *,
        step: int
) -> None:
    """Обработать кнопок смены дня дневника. ``step`` это сдвиг дня (1 следующий, -1 предыдущий)."""

    if update.effective_message is None:
        raise TelegramBotError()

    data: dict = user['diary_week']
    next_index: int = data['current_weekday'] + step

    if next_index > 4:
        p_date = datetime.strptime(data['4'][0]['date'], '%d.%m.%Y')
        await get_diary(update, context, date=p_date.date(), delta=timedelta(3))
        user = get_user_from_db(update)
        data = user['diary_week']
        next_index = 0
    elif next_index < 0:
        p_date = datetime.strptime(data['0'][0]['date'], '%d.%m.%Y')
        await get_diary(update, context, date=p_date.date(), delta=timedelta(-3))
        user = get_user_from_db(update)
        data = user['diary_week']
        next_index = 4

    user['diary_week']['current_weekday'] = next_index
    update_db(user, update)

    reply_markup = InlineKeyboardMarkup([*DIARY_BUTTONS])
    send_text: str = f"*{data[str(next_index)][0]['date']}*"
    for diary_lesson in data[str(next_index)]:
        send_text += DIARY_LESSON_TEMPLATE.format(**diary_lesson)
    await update.effective_message.edit_text(send_text, parse_mode='Markdown', reply_markup=reply_markup)


async def process_homework(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        user: dict,
        *,
        step: int
) -> None:
    """Обработать кнопок смены дня домашнего задания. ``step`` это сдвиг дня (1 следующий, -1 предыдущий)."""

    if update.effective_message is None:
        raise TelegramBotError()

    data: dict = user['homework_week']
    next_index: int = data['current_weekday'] + step

    if next_index > 4:
        p_date = datetime.strptime(data['4'][0]['date'], '%d.%m.%Y')
        await get_homework(update, context, date=p_date.date(), delta=timedelta(3))
        user = get_user_from_db(update)
        data = user['homework_week']
        next_index = 0
    elif next_index < 0:
        p_date = datetime.strptime(data['0'][0]['date'], '%d.%m.%Y')
        await get_homework(update, context, date=p_date.date(), delta=timedelta(-3))
        user = get_user_from_db(update)
        data = user['homework_week']
        next_index = 4

    user['homework_week']['current_weekday'] = next_index
    update_db(user, update)

    reply_markup = InlineKeyboardMarkup([*HOMEWORK_BUTTONS])
    send_text: str = f"*{data[str(next_index)][0]['date']}*"
    for homework_lesson in data[str(next_index)]:
        send_text += HOMEWORK_LESSON_TEMPLATE.format(**homework_lesson)
    await update.effective_message.edit_text(send_text, parse_mode='Markdown', reply_markup=reply_markup)


async def process_schedule(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        user: dict,
        *,
        step: int
) -> None:
    """Обработать кнопок смены дня расписания. ``step`` это сдвиг дня (1 следующий, -1 предыдущий)."""
    
    if update.effective_message is None:
        raise TelegramBotError()

    data: dict = user['schedule_week']
    next_index = data['current_weekday'] + step

    if next_index > 4:
        p_date = datetime.strptime(data['4'][0]['date'], '%d.%m.%Y')
        await get_schedule_day(update, context, date=p_date.date(), delta=timedelta(3))
        user = get_user_from_db(update)
        data = user['schedule_week']
        next_index = 0
    elif next_index < 0:
        p_date = datetime.strptime(data['0'][0]['date'], '%d.%m.%Y')
        await get_schedule_day(update, context, date=p_date.date(), delta=timedelta(-3))
        user = get_user_from_db(update)
        data = user['schedule_week']
        next_index = 4

    user['schedule_week']['current_weekday'] = next_index
    update_db(user, update)

    reply_markup = InlineKeyboardMarkup([*SCHEDULE_DAY_BUTTONS])
    send_text: str = f"*{data[str(next_index)][0]['date']}*"
    for schedule in data[str(next_index)]:
        send_text += SCHEDULE_DAY_TEMPLATE.format(**schedule)
    await update.effective_message.edit_text(send_text, parse_mode='Markdown', reply_markup=reply_markup)
