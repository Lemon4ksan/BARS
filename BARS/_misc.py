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
