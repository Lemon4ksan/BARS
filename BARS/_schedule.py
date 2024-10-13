from dataclasses import dataclass
from collections.abc import Sequence
from typing import Optional

from ._base import ClientObject

@dataclass
class ScheduleLesson(ClientObject):
    """Класс, представляющий урок из дневника.

    Attributes:
        id (:obj:`int`, optional): Уникальный идентификатор задания. Может быть пустым.
        date (:obj:`str`): Дата формата День-Месяц-Год.
        discipline (:obj:`str`): Название урока.
        has_auth_sferum (:obj:`bool`, optional): Есть ли регистрация в Сферум. Может быть пустым.
        index (:obj:`int`): Порядок урока в расписании.
        is_control_work (:obj:`bool`): Является ли работа контрольной.
        office (:obj:`str`, optional): Кабинет проведения урока. Может быть пустым.
        study_time_name (:obj:`str`, optional): Название временной смены. Может быть пустым.
        study_time_shift (:obj:`int`, optional): Временная смена. Может быть пустым.
        teacher (:obj:`str`, optional): Учитель, проводящий урок. Может быть пустым.
        time_begin (:obj:`str`, optional): Часы-Минуты начала урока. Может быть пустым.
        time_end (:obj:`str`, optional): Часы-Минуты конца урока. Может быть пустым.
    """

    date: str
    discipline: str
    index: int
    is_control_work: bool
    id: Optional[int] = None
    has_auth_sferum: Optional[bool] = None
    office: Optional[str] = None
    study_time_name: Optional[str] = None
    study_time_shift: Optional[int] = None
    teacher: Optional[str] = None
    time_begin: Optional[str] = None
    time_end: Optional[str] = None

    @classmethod
    def de_json(
            cls: dataclass,
            data: dict,
    ) -> 'ScheduleLesson':
        """Десериализация объекта.

        Args:
            data (:obj:`dict`): Поля и значения десериализуемого объекта.

        Returns:
            :class:`steam_trader.DiaryLesson`, optional: Урок из дневника.
        """

        data = super(ScheduleLesson, cls).de_json(data)

        return cls(**data)
@dataclass
class ScheduleDay(ClientObject):
    """Класс, представляющий расписание на день.

        Attributes:
            date (:obj:`str`): Дата формата Год-Месяц-День.
            lessons (Sequence[:class:`BARS.DiaryLesson`, optional], optional): Уроки на этот день.
                None, если выходной или каникулы.
            is_weekend (:obj:`bool`): Является ли данный день выходным.
        """

    date: str
    lessons: Sequence['ScheduleLesson']
    is_weekend: bool = False
    is_vacation: bool = False

    @classmethod
    def de_json(
            cls: dataclass,
            data: dict,
    ) -> 'ScheduleDay':
        """Десериализация объекта.

        Args:
            data (:obj:`dict`): Поля и значения десериализуемого объекта.

        Returns:
            :class:`steam_trader.DiaryDay`, optional: День из дневника.
        """

        try:
            for i, lesson in enumerate(data['lessons']):
                data['lessons'][i] = ScheduleLesson.de_json(lesson)
        except KeyError:
            data['lessons'] = []
        data = super(ScheduleDay, cls).de_json(data)

        return cls(**data)

@dataclass
class ScheduleMonth(ClientObject):
    """Класс, представляющий расписание на день.

        Attributes:
            days (Sequence[:class:`BARS.ScheduleDay`]): Последовательность дней недели.
            index (:obj:`int`): Порядок недели.
    """

    days: Sequence['ScheduleDay']
    index: int

    @classmethod
    def de_json(
            cls: dataclass,
            data: dict,
    ) -> 'ScheduleMonth':
        """Десериализация объекта.

        Args:
            data (:obj:`dict`): Поля и значения десериализуемого объекта.

        Returns:
            :class:`steam_trader.DiaryDay`, optional: День из дневника.
        """

        for i, day in enumerate(data['days']):
            data['days'][i] = ScheduleDay.de_json(day)

        data = super(ScheduleMonth, cls).de_json(data)

        return cls(**data)
