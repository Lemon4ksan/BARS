from dataclasses import dataclass
from collections.abc import Sequence
from typing import Optional

from ._base import ClientObject

@dataclass(slots=True)
class ScheduleLesson(ClientObject):
    """Класс, представляющий урок из дневника.

    Attributes:
        id (`int`, optional): Уникальный идентификатор задания. Может быть пустым.
        date (`str`): Дата формата День-Месяц-Год.
        discipline (`str`): Название урока.
        has_auth_sferum (`bool`, optional): Есть ли регистрация в Сферум. Может быть пустым.
        index (`int`): Порядок урока в расписании.
        is_control_work (`bool`): Является ли работа контрольной.
        office (`str`, optional): Кабинет проведения урока. Может быть пустым.
        study_time_name (`str`, optional): Название временной смены. Может быть пустым.
        study_time_shift (`int`, optional): Временная смена. Может быть пустым.
        teacher (`str`, optional): Учитель, проводящий урок. Может быть пустым.
        time_begin (`str`, optional): Часы-Минуты начала урока. Может быть пустым.
        time_end (`str`, optional): Часы-Минуты конца урока. Может быть пустым.
    """

    id: int
    date: str
    discipline: str
    index: int
    is_control_work: bool
    has_auth_sferum: Optional[bool] = None
    office: Optional[str] = None
    study_time_name: Optional[str] = None
    study_time_shift: Optional[int] = None
    teacher: Optional[str] = None
    time_begin: Optional[str] = None
    time_end: Optional[str] = None

    @classmethod
    def de_json(
            cls,
            data: dict,
    ) -> 'ScheduleLesson':

        data = super(ScheduleLesson, cls).de_json(data)
        data['id'] = data['id']  # Почему-то это исключает ошибку.

        return cls(**data)

@dataclass(slots=True)
class ScheduleDay(ClientObject):
    """Класс, представляющий расписание на день.

    Attributes:
        date (`str`): Дата формата Год-Месяц-День.
        lessons (Sequence[`BARS.DiaryLesson`, optional], optional): Уроки на этот день.
            None, если выходной или каникулы.
        is_weekend (`bool`): Является ли данный день выходным.
        """

    date: str
    lessons: Sequence[ScheduleLesson]
    is_weekend: bool = False
    is_vacation: bool = False

    @classmethod
    def de_json(
            cls,
            data: dict,
    ) -> 'ScheduleDay':
        try:
            for i, lesson in enumerate(data['lessons']):
                data['lessons'][i] = ScheduleLesson.de_json(lesson)
        except KeyError:
            data['lessons'] = []
        data = super(ScheduleDay, cls).de_json(data)

        return cls(**data)

@dataclass(slots=True)
class ScheduleMonth(ClientObject):
    """Класс, представляющий расписание на день.

    Attributes:
        days (Sequence[`BARS.ScheduleDay`]): Последовательность дней недели.
        index (`int`): Порядок недели.
    """

    days: Sequence[ScheduleDay]
    index: int

    @classmethod
    def de_json(
            cls,
            data: dict,
    ) -> 'ScheduleMonth':

        for i, day in enumerate(data['days']):
            data['days'][i] = ScheduleDay.de_json(day)

        data = super(ScheduleMonth, cls).de_json(data)

        return cls(**data)
