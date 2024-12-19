from collections.abc import Sequence
from datetime import date
from datetime import datetime

from BARS import DiaryDay, HomeworkDay, ScheduleDay
from .. import templates


def form_diary_send_text(diary_day: DiaryDay, f_time: str) -> str:
    """Сформировать текст для отправки в Телеграм."""

    send_text = f"*{f_time}*"
    for diary_lesson in diary_day.lessons:
        send_text += templates.DIARY_LESSON_TEMPLATE.format(
            discipline=diary_lesson.discipline,
            theme=f'\n{diary_lesson.theme}' if diary_lesson.theme else '',
            mark_info=f'\n{diary_lesson.mark} - {diary_lesson.mark_type}' if diary_lesson.mark else '',
            comment=f'\nКомментарий: {diary_lesson.comment}' if diary_lesson.comment else '',
            remarks=f'\nЗамечание: {diary_lesson.remarks}' if diary_lesson.remarks else '',
            attendance=f'\n{diary_lesson.attendance}' if diary_lesson.attendance else ''
        )
    return send_text


def proccess_diary(result_dict: dict, diary_days: Sequence[DiaryDay], _date: date) -> str:
    """Обновляет ``result_dict`` данными о неделе дневника и возвращает текст для отправки в Телеграм."""

    send_text: str = ''
    for i, diary_day in enumerate(diary_days[:-2]):
        diary_day.remove_html_tags()

        # Перевод Г-М-Д на Д.М.Г
        f_time: str = datetime.strptime(diary_day.date, '%Y-%m-%d').strftime('%d.%m.%Y')
        if diary_day.date == str(_date):
            send_text = form_diary_send_text(diary_day, f_time)

        result_dict[i] = []
        for diary_lesson in diary_day.lessons:
            result_dict[i].append({
                'date': f_time,
                'discipline': diary_lesson.discipline,
                'theme': f'\n{diary_lesson.theme}' if diary_lesson.theme else '',
                'mark_info': f'\n{diary_lesson.mark} - {diary_lesson.mark_type}' if diary_lesson.mark else '',
                'comment': f'\nКомментарий: {diary_lesson.comment}' if diary_lesson.comment else '',
                'remarks': f'\nЗамечание: {diary_lesson.remarks}' if diary_lesson.remarks else '',
                'attendance': f'\n{diary_lesson.attendance}' if diary_lesson.attendance else ''
            })
    return send_text


def form_homework_send_text(homework_day: HomeworkDay, f_time: str, base_url: str) -> str:
    """Сформировать текст для отправки в Телеграм."""

    send_text = f"*{f_time}*"
    for homework_lesson in homework_day.homeworks:
        ttc: str = f'({homework_lesson.homework_time_to_complete} мин)'
        materials: list = [
            f'\n[{material['name']}]({base_url[:-1] + material['url']})' for material in homework_lesson.materials
        ]  # Здесь используется гиперссылка.

        send_text += templates.HOMEWORK_LESSON_TEMPLATE.format(
            discipline=homework_lesson.discipline,
            homework=homework_lesson.homework if homework_lesson.homework else 'Нет',
            time_to_complete=ttc if homework_lesson.homework_time_to_complete else '',
            materials='\nПрикреплённые сслыки: ' + '\n'.join(materials) if materials else ''
        )
    return send_text


def proccess_homework(result_dict: dict, homework_days: Sequence[HomeworkDay], base_url: str, _date: date) -> str:
    """Обновляет ``result_dict`` данными о неделе домашнего задания и возвращает текст для отправки в Телеграм."""

    send_text: str = ''
    for i, homework_day in enumerate(homework_days[:-2]):
        homework_day.remove_html_tags()

        # Перевод Г-М-Д на Д.М.Г
        f_time: str = datetime.strptime(homework_day.homeworks[0].date, '%Y-%m-%d').strftime('%d.%m.%Y')

        if homework_day.date == str(_date):
            send_text = form_homework_send_text(homework_day, f_time, base_url)
        result_dict[i] = []
        for homework_lesson in homework_day.homeworks:
            ttc: str = f'({homework_lesson.homework_time_to_complete} мин)'

            materials: list = [
                f'\n[{material['name']}]({base_url[:-1] + material['url']})' for material in homework_lesson.materials
            ]  # Здесь используется гиперссылка.

            result_dict[i].append({
                'date': f_time,
                'discipline': homework_lesson.discipline,
                'homework': homework_lesson.homework if homework_lesson.homework else 'Нет',
                'time_to_complete': ttc if homework_lesson.homework_time_to_complete else '',
                'materials': '\nПрикреплённые сслыки: ' + '\n'.join(materials) if materials else ''
            })

    return send_text


def form_schedule_send_text(schedule_day: ScheduleDay, f_time: str) -> str:
    """Сформировать текст для отправки в Телеграм."""

    send_text: str = f"*{f_time}*"
    for lesson in schedule_day.lessons:
        begin = lesson.time_begin
        end = lesson.time_end
        send_text += templates.SCHEDULE_DAY_TEMPLATE.format(
            discipline=lesson.discipline,
            teacher=lesson.teacher,
            office=lesson.office,
            start=begin[:-3] if begin is not None else "",
            end=end[:-3] if end is not None else "",
        )
    return send_text


def proccess_schedule(result_dict: dict, schedule_days: Sequence[ScheduleDay], _date: date) -> str:
    """Обновляет ``result_dict`` данными о расписании на неделю и возвращает текст для отправки в Телеграм."""

    send_text: str = ""
    for i, schedule_day in enumerate(schedule_days[:-2]):
        schedule_day.remove_html_tags()

        # Перевод Г-М-Д на Д.М.Г
        f_time: str = datetime.strptime(schedule_day.lessons[0].date, '%Y-%m-%d').strftime('%d.%m.%Y')

        if schedule_day.date == str(_date):
            send_text = form_schedule_send_text(schedule_day, f_time)

        result_dict[i] = []
        for lesson in schedule_day.lessons:
            begin = lesson.time_begin
            end = lesson.time_end
            result_dict[i].append({
                'date': f_time,
                'discipline': lesson.discipline,
                'teacher': lesson.teacher,
                'start': begin[:-3] if begin is not None else "",
                'end': end[:-3] if end is not None else "",
                'office': lesson.office
            })

    return send_text
