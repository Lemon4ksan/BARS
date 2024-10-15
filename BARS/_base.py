import dataclasses
import logging
import re
from bs4 import BeautifulSoup
from abc import ABCMeta
from dataclasses import dataclass
from typing import Optional, TypeVar
from collections.abc import MutableSequence

_BT = TypeVar('_BT')

class ClientObject:
    """Базовый класс для всех объектов библиотеки."""

    __metaclass__ = ABCMeta

    def remove_html_tags(self, __obj: _BT = '__dataclass__', *, replace_p_with='\n') -> _BT:
        """Преобразует словари, изменяемые последовательности, классы и строки в читабельный формат, без HTML тегов.
        Также заменяет теги <a> на гиперссылки для отправки в Телеграм.

        Аргумент ``replace_p_with`` заменяет теги <p> на введённый символ. По умолчанию новая строка.

        Возвращаемый предмет зависит от типа данных __obj. Не меняйте __obj если используете на датаклассе.
        """

        if __obj == '__dataclass__':
            __obj = self

        if isinstance(__obj, str):
            links = re.findall(r'<a href="[^"]+">.+[</a>]', __obj)
            for link in links:  # Заменяет теги <a> на гиперссылки
                tag = BeautifulSoup(link, 'lxml').find('a')
                __obj = __obj.replace(link, f'[{tag.text}]({tag.get('href')}) ')
            __obj = re.sub(r'<[^>]+>', '', __obj.replace('<p', f'{replace_p_with}<p'))
            if replace_p_with == ' ':
                __obj = __obj.replace('  ', ' ')  # исключаем двойные <p>
            return __obj.strip()
        elif isinstance(__obj, MutableSequence):
            for i, item in enumerate(__obj):
                __obj[i] = self.remove_html_tags(item)
        elif isinstance(__obj, dict):
            for k, v in __obj.copy().items():
                __obj[k] = self.remove_html_tags(v)
        elif dataclasses.is_dataclass(__obj):
            for f in dataclasses.fields(__obj):
                __obj.__setattr__(f.name, self.remove_html_tags(__obj.__getattribute__(f.name)))

        return __obj

    @classmethod
    def de_json(cls: dataclass, data: dict) -> Optional[dict]:
        """Десериализация объекта.

        Args:
            data (:obj:`dict`): Поля и значения десериализуемого объекта.

        Returns:
            :obj:`dict`, optional: Словарь с валидными аттрибутами для создания датакласса.
        """

        data = data.copy()

        fields = {f.name for f in dataclasses.fields(cls)}

        cleaned_data = {}
        unknown_data = {}

        for k, v in data.items():
            if k in fields:
                cleaned_data[k] = v
            else:
                unknown_data[k] = v

        if unknown_data:
            logging.warning(f'Были получены неизвестные аттриубты для класса {cls} :: {unknown_data}')

        return cleaned_data
