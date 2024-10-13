import logging
import traceback
from datetime import datetime, timedelta

from telegram import Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes

import BARS
import templates
import utils
from BARS import BClientAsync
from BARS import exceptions
from utils import get_user_from_db, update_db

from commands import get_diary, get_homework, get_schedule_day

async def handle_exception(update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик исключений."""

    if isinstance(context.error, KeyError):  # wildcard
        user: dict = get_user_from_db(update)
        for key in templates.USER_DICT:
            if key not in user.keys():
                user[key] = None
        logging.error("".join(traceback.format_exception(None, context.error, context.error.__traceback__)))
        update_db(user, update)
        await update.message.reply_text('❌ Внутренняя ошибка. Попробуйте ещё раз')
    elif isinstance(context.error, exceptions.Unauthorized):
        await update.message.reply_text('❌ Недействительный sessionid. Обновите его с помощью /set_sessionid')
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f'❌ Произошла неизвестная ошибка:\n {str(context.error)}'
        )
        logging.error("".join(traceback.format_exception(None, context.error, context.error.__traceback__)))


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик содержимого сообщений по current_operation в датабазе."""

    user: dict = get_user_from_db(update)
    match user['current_operation']:
        case 'sessionid':  # /set_sessionid
            async with BClientAsync(update.message.text) as client:
                pupil_info: 'BARS.PupilInfo' = await client.get_pupil_info()
                acount_info: 'BARS.AccountInfo' = await client.get_account_info()
            await update.message.reply_text(f'Привет, {pupil_info.user_fullname.split()[1]}!')

            user['sessionid'] = update.message.text
            user['pupilid'] = acount_info.pupilid

        case 'progressdata':  # /get_progress_data
            async with BClientAsync(user['sessionid']) as client:
                account: 'BARS.AccountInfo' = await client.get_account_info()
                if update.message.text.lower() == 'все':
                    subjectid: int = 0
                    send_text: str = "Общие данные:\n"
                else:
                    for discipline in account.disciplines:
                        if update.message.text.lower() in discipline.name.lower():
                            subjectid: int = discipline.id
                            send_text: str = f"Данные для {discipline.name}\n"
                            break
                    else:
                        await update.message.reply_text(f'❌ Недоступный предмет "{update.message.text}"')
                        return

                progress_data: 'BARS.ProgressData' = await client.get_progress_data(
                    user['pupilid'],
                    f"{utils.get_school_start_year()}-09-01",
                    f"{utils.get_school_start_year() + 1}-08-31",
                    subjectid
                )

            for date, mark in zip(progress_data.dates, progress_data.series[0].data):
                send_text += f"*{date}*: {round(mark, 2)}\n"

            await update.message.reply_text(send_text, parse_mode='Markdown')

        case 'attendancedata':  # /get_attendance_data
            async with BClientAsync(user['sessionid']) as client:
                account: 'BARS.AccountInfo' = await client.get_account_info()
                if update.message.text.lower() == 'все':
                    subjectid: int = 0
                    send_text: str = "Общие данные:\n"
                else:
                    for discipline in account.disciplines:
                        if update.message.text.lower() in discipline.name.lower():
                            subjectid: int = discipline.id
                            send_text: str = f"Данные для {discipline.name}\n"
                            break
                    else:
                        await update.message.reply_text(f'❌ Недоступный предмет "{update.message.text}"')
                        return

                attendance_data: 'BARS.AttendaceData' = await client.get_attendace_data(
                    user['pupilid'],
                    f"{utils.get_school_start_year()}-09-01",
                    f"{utils.get_school_start_year() + 1}-08-31",
                    subjectid
                )

                send_text += templates.ATTENDANCE_TEMPLATE.format(
                    attendance_data.absent,
                    attendance_data.absent_good,
                    attendance_data.absent_bad,
                    attendance_data.ill
                )

                await update.message.reply_text(send_text)

    user['current_operation'] = None
    update_db(user, update)


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработка ответов Inline клавиатуры."""

    user: dict = get_user_from_db(update)
    match update.callback_query.data:
        case 'total_marks_subperiod1':
            reply_markup = InlineKeyboardMarkup([
                [templates.TOTAL_MARKS_BUTTONS[1], templates.TOTAL_MARKS_BUTTONS[2]],
                [templates.TOTAL_MARKS_BUTTONS[3]]
            ])
            await update.effective_message.edit_text(user['total_marks']['0'], reply_markup=reply_markup)
        case 'total_marks_subperiod2':
            reply_markup = InlineKeyboardMarkup([
                [templates.TOTAL_MARKS_BUTTONS[0], templates.TOTAL_MARKS_BUTTONS[2]],
                [templates.TOTAL_MARKS_BUTTONS[3]]
            ])
            await update.effective_message.edit_text(user['total_marks']['1'], reply_markup=reply_markup)
        case 'total_marks_subperiod3':
            reply_markup = InlineKeyboardMarkup([
                [templates.TOTAL_MARKS_BUTTONS[0], templates.TOTAL_MARKS_BUTTONS[1]],
                [templates.TOTAL_MARKS_BUTTONS[3]]
            ])
            await update.effective_message.edit_text(user['total_marks']['2'], reply_markup=reply_markup)
        case 'total_marks_subperiod4':
            reply_markup = InlineKeyboardMarkup([
                [templates.TOTAL_MARKS_BUTTONS[0], templates.TOTAL_MARKS_BUTTONS[1]],
                [templates.TOTAL_MARKS_BUTTONS[2]]
            ])
            await update.effective_message.edit_text(user['total_marks']['3'], reply_markup=reply_markup)
        case 'schedule_previous_day':
            data: dict = user['schedule_week']
            next_index = data['current_weekday'] - 1

            if next_index < 0:
                p_date = datetime.strptime(data['0'][0]['date'], '%d.%m.%Y')
                await get_schedule_day(update, context, date=p_date.date(), delta=timedelta(-3))
                user: dict = get_user_from_db(update)
                data: dict = user['schedule_week']
                next_index = 4
            reply_markup = InlineKeyboardMarkup([templates.SCHEDULE_DAY_BUTTONS])

            user['schedule_week']['current_weekday'] = next_index
            update_db(user, update)

            send_text: str = f"*{data[str(next_index)][0]['date']}*"
            for schedule in data[str(next_index)]:
                send_text += templates.SCHEDULE_DAY_TEMPLATE.format(**schedule)
            await update.effective_message.edit_text(send_text, parse_mode='Markdown', reply_markup=reply_markup)
        case 'schedule_next_day':
            data: dict = user['schedule_week']
            next_index = data['current_weekday'] + 1

            if next_index > 4:
                p_date = datetime.strptime(data['4'][0]['date'], '%d.%m.%Y')
                await get_schedule_day(update, context, date=p_date.date(), delta=timedelta(3))
                user: dict = get_user_from_db(update)
                data: dict = user['schedule_week']
                next_index = 0
            reply_markup = InlineKeyboardMarkup([templates.SCHEDULE_DAY_BUTTONS])

            user['schedule_week']['current_weekday'] = next_index
            update_db(user, update)

            send_text: str = f"*{data[str(next_index)][0]['date']}*"
            for schedule in data[str(next_index)]:
                send_text += templates.SCHEDULE_DAY_TEMPLATE.format(**schedule)
            await update.effective_message.edit_text(send_text, parse_mode='Markdown', reply_markup=reply_markup)

        case 'homework_previous_day':
            data: dict = user['homework_week']
            next_index = data['current_weekday'] - 1

            if next_index < 0:
                p_date = datetime.strptime(data['0'][0]['date'], '%d.%m.%Y')
                await get_homework(update, context, date=p_date.date(), delta=timedelta(-3))
                user: dict = get_user_from_db(update)
                data: dict = user['homework_week']
                next_index = 4
            reply_markup = InlineKeyboardMarkup([templates.HOMEWORK_BUTTONS])

            user['homework_week']['current_weekday'] = next_index
            update_db(user, update)

            send_text: str = f"*{data[str(next_index)][0]['date']}*"
            for homework_lesson in data[str(next_index)]:
                send_text += templates.HOMEWORK_LESSON_TEMPLATE.format(**homework_lesson)
            await update.effective_message.edit_text(send_text, parse_mode='Markdown', reply_markup=reply_markup)

        case 'homework_next_day':
            data: dict = user['homework_week']
            next_index = data['current_weekday'] + 1

            if next_index > 4:
                p_date = datetime.strptime(data['4'][0]['date'], '%d.%m.%Y')
                await get_homework(update, context, date=p_date.date(), delta=timedelta(3))
                user: dict = get_user_from_db(update)
                data: dict = user['homework_week']
                next_index = 0
            reply_markup = InlineKeyboardMarkup([templates.HOMEWORK_BUTTONS])

            user['homework_week']['current_weekday'] = next_index
            update_db(user, update)

            send_text: str = f"*{data[str(next_index)][0]['date']}*"
            for homework_lesson in data[str(next_index)]:
                send_text += templates.HOMEWORK_LESSON_TEMPLATE.format(**homework_lesson)
            await update.effective_message.edit_text(send_text, parse_mode='Markdown', reply_markup=reply_markup)

        case 'diary_previous_day':
            data: dict = user['diary_week']
            next_index = data['current_weekday'] - 1

            if next_index < 0:
                p_date = datetime.strptime(data['0'][0]['date'], '%d.%m.%Y')
                await get_diary(update, context, date=p_date.date(), delta=timedelta(-3))
                user: dict = get_user_from_db(update)
                data: dict = user['diary_week']
                next_index = 4
            reply_markup = InlineKeyboardMarkup([templates.DIARY_BUTTONS])

            user['diary_week']['current_weekday'] = next_index
            update_db(user, update)

            send_text: str = f"*{data[str(next_index)][0]['date']}*"
            for diary_lesson in data[str(next_index)]:
                send_text += templates.DIARY_LESSON_TEMPLATE.format(**diary_lesson)
            await update.effective_message.edit_text(send_text, parse_mode='Markdown', reply_markup=reply_markup)

        case 'diary_next_day':
            data: dict = user['diary_week']
            next_index = data['current_weekday'] + 1

            if next_index > 4:
                p_date = datetime.strptime(data['4'][0]['date'], '%d.%m.%Y')
                await get_diary(update, context, date=p_date.date(), delta=timedelta(3))
                user: dict = get_user_from_db(update)
                data: dict = user['diary_week']
                next_index = 0
            reply_markup = InlineKeyboardMarkup([templates.DIARY_BUTTONS])

            user['diary_week']['current_weekday'] = next_index
            update_db(user, update)

            send_text: str = f"*{data[str(next_index)][0]['date']}*"
            for diary_lesson in data[str(next_index)]:
                send_text += templates.DIARY_LESSON_TEMPLATE.format(**diary_lesson)
            await update.effective_message.edit_text(send_text, parse_mode='Markdown', reply_markup=reply_markup)
