import logging
import traceback
from datetime import datetime, timedelta

from telegram import Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes

import templates
from BARS import exceptions
from commands import get_diary, get_homework, get_schedule_day
from utils.general import get_user_from_db, update_db
from utils.handlers_utils import (
    process_sessionid, process_progressdata, process_attendancedata,
    process_diary, update_diary,
    process_homework, update_homework,
    process_schedule, update_schedule
)


async def handle_exception(update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик исключений."""

    if isinstance(context.error, KeyError):  # wildcard
        user: dict = get_user_from_db(update)
        for key in templates.USER_DICT.keys():
            if key not in user.keys():
                user[key] = None
        logging.error("".join(traceback.format_exception(None, context.error, context.error.__traceback__)))
        update_db(user, update)
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='❌ Внутренняя ошибка. Попробуйте ещё раз'
        )
    elif isinstance(context.error, exceptions.Unauthorized):
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='❌ Недействительный sessionid. Обновите его с помощью /set_sessionid'
        )
    elif isinstance(context.error, exceptions.InternalError):
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f'❌ В данный момент сайт недоступен. Повторите попытку позже.'
        )
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
        case 'sessionid':
            await process_sessionid(update, user)
        case 'attendancedata':
            await process_attendancedata(update, user)
        case 'progressdata':
            await process_progressdata(update, user)

    user['current_operation'] = None
    update_db(user, update)


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработка ответов Inline клавиатуры."""

    user: dict = get_user_from_db(update)
    match update.callback_query.data:
        case 'diary_next_day':
            await process_diary(update, context, user, step=1)
        case 'diary_previous_day':
            await process_diary(update, context, user, step=-1)
        case 'update_diary':
            await update_diary(update, context, user)
        case 'homework_next_day':
            await process_homework(update, context, user, step=1)
        case 'homework_previous_day':
            await process_homework(update, context, user, step=-1)
        case 'update_homework':
            await update_homework(update, context, user)
        case 'schedule_next_day':
            await process_schedule(update, context, user, step=1)
        case 'schedule_previous_day':
            await process_schedule(update, context, user, step=-1)
        case 'update_schedule':
            await update_schedule(update, context, user)
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
