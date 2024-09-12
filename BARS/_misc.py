from dataclasses import dataclass

from ._base import ClientObject

@dataclass
class Event(ClientObject):
    """Класс, представляющий праздник.

    Attributes:
        date (:obj:`str`): Дата формата Год-Месяц-День.
        date_str (:obj:`str`): Дата формата День-Месяц-Год.
        theme (:obj:`str`): Название праздника.
    """

    date: str
    date_str: str
    theme: str

    @classmethod
    def de_json(
            cls: dataclass,
            data: dict,
    ) -> 'Event':
        """Десериализация объекта.

        Args:
            data (:obj:`dict`): Поля и значения десериализуемого объекта.

        Returns:
            :class:`BARS.Event`: Праздник.
        """

        data = super(Event, cls).de_json(data)

        return cls(**data)

@dataclass
class Birthday(ClientObject):
    """Класс, представляющий день рождения.

    Attributes:
        date (:obj:`str`): Дата формата Год-Месяц-День.
        male (:obj:`bool`): Является ли именинник мужчиной.
        photo (:obj:`str`): Неабсолютная ссылка на фото ученика.
        short_name (:obj:`str`): Фамилия И.О.
    """

    date: str
    male: bool
    photo: str
    short_name: str

    @classmethod
    def de_json(
            cls: dataclass,
            data: dict,
    ) -> 'Birthday':
        """Десериализация объекта.

        Args:
            data (:obj:`dict`): Поля и значения десериализуемого объекта.

        Returns:
            :class:`BARS.Birthday`: День рождения.
        """

        data = super(Birthday, cls).de_json(data)

        return cls(**data)
