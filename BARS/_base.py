import dataclasses
import logging
import keyword
import json
import re
from abc import ABCMeta
from dataclasses import dataclass
from typing import Any, Optional, TypeVar
from collections.abc import MutableSequence

reserved_names = keyword.kwlist

_BT = TypeVar('_BT')

class ClientObject:
    """Базовый класс для всех объектов библиотеки."""

    __metaclass__ = ABCMeta

    def remove_html_tags(self, __obj: _BT = '__dataclass__', *, replace_p_with='\n') -> _BT:
        """Преобразует словари, изменяемые последовательности, классы и строки в читабельный формат, без HTML тегов.

        Аргумент ``replace_p_with`` заменяет теги <p> на введённый символ. По умолчанию новая строка.

        Возвращаемый предмет зависит от типа данных __obj. Не меняйте __obj если используете на датаклассе.
        """

        if __obj == '__dataclass__':
            __obj = self

        if isinstance(__obj, str):
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

    def to_json(self, for_request: bool = False) -> str:
        """Сериализация объекта.

        Args:
            for_request (:obj:`bool`): Подготовить ли объект для отправки в теле запроса.

        Returns:
            :obj:`str`: Сериализованный в JSON объект.
        """
        return json.dumps(self.to_dict(for_request), ensure_ascii=False)

    def to_dict(self, for_request: bool = False) -> dict:
        """Рекурсивная сериализация объекта.

        Args:
            for_request (:obj:`bool`): Перевести ли обратно все поля в camelCase и игнорировать зарезервированные слова.

        Note:
            Исключает из сериализации `client` и `_id_attrs` необходимые в `__eq__`.

            К зарезервированным словам добавляет "_" в конец.

        Returns:
            :obj:`dict`: Сериализованный в dict объект.
        """

        def parse(val: Any) -> Any:
            if hasattr(val, 'to_dict'):
                return val.to_dict(for_request)
            if isinstance(val, list):
                return [parse(it) for it in val]
            if isinstance(val, dict):
                return {key: parse(value) for key, value in val.items()}
            return val

        data = self.__dict__.copy()

        if for_request:
            for k, v in data.copy().items():
                camel_case = ''.join(word.title() for word in k.split('_'))
                camel_case = camel_case[0].lower() + camel_case[1:]

                data.pop(k)
                data.update({camel_case: v})
        else:
            for k, v in data.copy().items():
                if k.lower() in reserved_names:
                    data.pop(k)
                    data.update({f'{k}_': v})

        return parse(data)
