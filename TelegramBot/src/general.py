import json
from datetime import datetime
from pathlib import Path
from typing import Optional
from telegram import Update

from .exceptions import TelegramBotError

DB_PATH: Path = Path.cwd() / 'TelegramBot' / 'db.json'

def get_user_from_db(update: Update) -> dict:
    """Получить поля пользователя из датабазы."""
    if update.effective_user is None:
        raise TelegramBotError("Не удалось получить запись из датабазы. Неизвестный пользователь.")
    with open(DB_PATH, 'r') as f:
        contents: dict[str, dict] = dict(json.load(f))
        return contents[str(update.effective_user.id)]


def update_db(dictionary: dict, update: Optional[Update] = None) -> None:
    """Обновить датабазу. Если update не указан, датабаза становиться данным словарём."""

    with open(DB_PATH, 'r') as f:
        contents: dict[str, dict] = dict(json.load(f))

    if update:
        if update.effective_user is None:
            raise TelegramBotError()

        contents[str(update.effective_user.id)] = dictionary
        with open(DB_PATH, 'w') as f:
            json.dump(contents, f)
    else:
        with open(DB_PATH, 'w') as f:
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