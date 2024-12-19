from dataclasses import dataclass
from collections.abc import Sequence
from typing import Optional

from ._base import ClientObject

@dataclass(slots=True)
class DiaryLesson(ClientObject):
    """Класс, представляющий урок из дневника.

    Attributes:
        id (`int`): Уникальный идентификатор задания.
        date (`str`): Дата формата Год-Месяц-День.
        attendance (`str`): Замечание об отсутствии на занятии.
        comment (`str`): Комментарий оценки.
        discipline (`str`): Название урока.
        homework_time_to_complete (`int`): Время на выполнения д/з.
        ind_homework_exists (`bool`): Присутствует ли индивидуальное д/з.
        index (`int`): Порядок урока в расписании.
        is_control_work (`bool`): Является ли урок контрольным.
        mark (`str`): Оценка.
        mark_type (`str`): Тип оценки.
        materials (Sequence[`str`]): Неабсолютные ссылки на прикреплённые файлы.
        office (`str`): Кабинет проведения урока.
        remarks (`str`): Замечания.
        schedulelessontype (`str`): Вид работы.
        study_time_name (`str`): Название смены.
        study_time_shift (`int`): Номер смены.
        teacher (`str`): Учитель, проводящий урок.
        theme (`str`): Тема урока.
        time_begin (`str`): Часы-Минуты начала урока.
        time_end (`str`): Часы-Минуты конца урока.
    """

    id: int
    date: str
    attendance: str
    comment: str
    discipline: str
    homework: str
    homework_time_to_complete: int
    ind_homework_exists: bool
    index: int
    is_control_work: bool
    mark: str
    mark_type: str
    materials: Sequence[str]
    office: str
    remarks: str
    schedulelessontype: str
    study_time_name: str
    study_time_shift: int
    teacher: str
    theme: str
    time_begin: str
    time_end: str

    @classmethod
    def de_json(
            cls,
            data: dict,
    ) -> 'DiaryLesson':

        data = super(DiaryLesson, cls).de_json(data)

        return cls(**data)

@dataclass(slots=True)
class DiaryDay(ClientObject):
    """Класс, представляющий день из дневника.

    Attributes:
        date (`str`): Дата формата Год-Месяц-День.
        lessons (Sequence[`BARS.DiaryLesson`, optional], optional): Уроки на этот день.
            None, если выходной или каникулы.
        is_weekend (`bool`): Является ли данный день выходным.
        is_vacation (`bool`): Является ли данный день праздником/частью каникул.
    """

    date: str
    lessons: Sequence[DiaryLesson]
    is_weekend: bool = False
    is_vacation: bool = False

    @classmethod
    def de_json(
            cls,
            data: dict,
    ) -> 'DiaryDay':

        try:
            for i, lesson in enumerate(data['lessons']):
                data['lessons'][i] = DiaryLesson.de_json(lesson)
        except KeyError:
            data['lessons'] = []

        data = super(DiaryDay, cls).de_json(data)

        return cls(**data)
