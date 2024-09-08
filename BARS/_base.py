import dataclasses
import logging
from abc import ABCMeta
from dataclasses import dataclass
from typing import Any, Optional, Union

try:
    import ujson as json

    ujson = True
except ImportError:
    import json

class ClientObject:
    """Базовый класс для всех объектов библиотеки."""

    __metaclass__ = ABCMeta

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
