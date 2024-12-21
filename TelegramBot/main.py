import os
import logging
import coloredlogs

if os.path.basename(os.getcwd()) == 'TelegramBot':  # если venv не настроен
    os.chdir('..')

from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler
from telegram.ext.filters import ALL

from src.commands import *
from src.handlers import handle_message, handle_callback, handle_exception

if __name__ == '__main__':
    logging.basicConfig(level=logging.WARNING)
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('BARS').setLevel(logging.WARNING)
    coloredlogs.install()

    load_dotenv()
    token = os.getenv('TELEGRAM_TOKEN')
    if token is None:
        raise ValueError('Токен должен быть указан в переменных среды.')
    application = ApplicationBuilder().token(token).build()

    start_handler = CommandHandler(('start', 'help'), start)
    set_sessionid_handler = CommandHandler('set_sessionid', set_sessionid)
    get_diary_handler = CommandHandler('get_diary', get_diary)
    get_homework_handler = CommandHandler('get_homework', get_homework)
    get_schedule_day_handler = CommandHandler('get_schedule_day', get_schedule_day)
    get_summary_marks_handler = CommandHandler('get_summary_marks', get_summary_marks)
    get_total_marks_handler = CommandHandler('get_total_marks', get_total_marks)
    get_attendance_data_handler = CommandHandler('get_attendance_data', get_attendance_data)
    get_progress_data_handler = CommandHandler('get_progress_data', get_progress_data)
    get_school_info_handler = CommandHandler('get_school_info', get_school_info)
    get_class_info_handler = CommandHandler('get_class_info', get_class_info)
    get_birthdays_handler = CommandHandler('get_birthdays', get_birthdays)
    get_events_handler = CommandHandler('get_events', get_events)

    message_handler = MessageHandler(ALL, handle_message)
    callback_handler = CallbackQueryHandler(handle_callback)

    application.add_handler(start_handler)
    application.add_handler(set_sessionid_handler)
    application.add_handler(get_diary_handler)
    application.add_handler(get_homework_handler)
    application.add_handler(get_schedule_day_handler)
    application.add_handler(get_summary_marks_handler)
    application.add_handler(get_total_marks_handler)
    application.add_handler(get_attendance_data_handler)
    application.add_handler(get_progress_data_handler)
    application.add_handler(get_school_info_handler)
    application.add_handler(get_class_info_handler)
    application.add_handler(get_birthdays_handler)
    application.add_handler(get_events_handler)
    application.add_handler(message_handler)
    application.add_handler(callback_handler)

    application.add_error_handler(handle_exception)  # type: ignore Странные тайп-хинты.

    application.run_polling()
