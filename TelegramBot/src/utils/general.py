import json
from typing import Optional
from datetime import datetime
from telegram import Update

def get_user_from_db(update: Update) -> dict:
    """Получить поля пользователя из датабазы."""
    with open('../db.json', 'r') as f:
        contents: dict[str, dict] = dict(json.load(f))
        return contents[str(update.effective_user.id)]


def update_db(dictionary: dict, update: Optional[Update] = None) -> None:
    """Обновить датабазу. Если update не указан, датабаза становиться данным словарём."""

    with open('../db.json', 'r') as f:
        contents: dict[str, dict] = dict(json.load(f))

    if update:
        contents[str(update.effective_user.id)] = dictionary
        with open('../db.json', 'w') as f:
            json.dump(contents, f)
    else:
        with open('../db.json', 'w') as f:
            json.dump(dictionary, f)


def escape_illegal_chars(_object: str) -> str:
    """Избежать все недопустимые символы из строки/массива для использования в Markdown.

    Не используйте с уже отформатированным текстом."""

    return _object.replace('[', r'\[') \
        .replace(']', r'\]') \
        .replace('*', r'\*') \
        .replace('_', r'\_') \
        .replace('`', r'\`') \
        .replace('-', r'\-') \
        .replace('=', r'\=')


def get_school_start_year() -> int:
    """Получить год начала учёбы."""
    time = datetime.now()
    if time.month < 9:
        return time.year - 1
    else:
        return time.year