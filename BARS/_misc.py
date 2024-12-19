from dataclasses import dataclass

from ._base import ClientObject

@dataclass(slots=True)
class Event(ClientObject):
    """Класс, представляющий праздник.

    Attributes:
        date (`str`): Дата формата Год-Месяц-День.
        date_str (`str`): Дата формата День-Месяц-Год.
        theme (`str`): Название праздника.
    """

    date: str
    date_str: str
    theme: str

    @classmethod
    def de_json(
            cls,
            data: dict,
    ) -> 'Event':

        data = super(Event, cls).de_json(data)

        return cls(**data)

@dataclass(slots=True)
class Birthday(ClientObject):
    """Класс, представляющий день рождения.

    Attributes:
        date (`str`): Дата формата Год-Месяц-День.
        male (`bool`): Является ли именинник мужчиной.
        photo (`str`): Неабсолютная ссылка на фото ученика.
        short_name (`str`): Фамилия И.О.
    """

    date: str
    male: bool
    photo: str
    short_name: str

    @classmethod
    def de_json(
            cls,
            data: dict,
    ) -> 'Birthday':

        data = super(Birthday, cls).de_json(data)

        return cls(**data)
