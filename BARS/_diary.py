from dataclasses import dataclass
from collections.abc import Sequence
from typing import Optional

from ._base import ClientObject

@dataclass
class DiaryLesson(ClientObject):
    """Класс, представляющий урок из дневника.

    Attributes:
        id (:obj:`int`): Уникальный идентификатор задания.
        date (:obj:`str`): Дата формата Год-Месяц-День.
        attendance (:obj:`str`): Замечание об отсутствии на занятии.
        comment (:obj:`str`): Комментарий оценки.
        discipline (:obj:`str`): Название урока.
        homework_time_to_complete (:obj:`int`): Время на выполнения д/з.
        ind_homework_exists (:obj:`bool`): Присутствует ли индивидуальное д/з.
        index (:obj:`int`): Порядок урока в расписании.
        is_control_work (:obj:`bool`): Является ли урок контрольным.
        mark (:obj:`str`): Оценка.
        mark_type (:obj:`str`): Тип оценки.
        materials (Sequence[:obj:`str`]): Неабсолютные ссылки на прикреплённые файлы.
        office (:obj:`str`): Кабинет проведения урока.
        remarks (:obj:`str`): Замечания.
        schedulelessontype (:obj:`str`): Вид работы.
        study_time_name (:obj:`str`): Название временной смены.
        study_time_shift (:obj:`int`): Временная смена.
        teacher (:obj:`str`): Учитель, проводящий урок.
        theme (:obj:`str`): Тема урока.
        time_begin (:obj:`str`): Часы-Минуты начала урока.
        time_end (:obj:`str`): Часы-Минуты конца урока.
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
            cls: dataclass,
            data: dict,
    ) -> 'DiaryLesson':
        """Десериализация объекта.

        Args:
            data (:obj:`dict`): Поля и значения десериализуемого объекта.

        Returns:
            :class:`steam_trader.DiaryLesson`, optional: Урок из дневника.
        """

        data = super(DiaryLesson, cls).de_json(data)

        return cls(**data)

@dataclass
class DiaryDay(ClientObject):
    """Класс, представляющий день из дневника.

    Attributes:
        date (:obj:`str`): Дата формата Год-Месяц-День.
        lessons (Sequence[:class:`BARS.DiaryLesson`, optional], optional): Уроки на этот день.
            None, если выходной или каникулы.
        is_weekend (:obj:`bool`): Является ли данный день выходным.
    """

    date: str
    lessons: Sequence['DiaryLesson']
    is_weekend: bool = False
    is_vacation: bool = False

    @classmethod
    def de_json(
            cls: dataclass,
            data: dict,
    ) -> 'DiaryDay':
        """Десериализация объекта.

        Args:
            data (:obj:`dict`): Поля и значения десериализуемого объекта.

        Returns:
            :class:`steam_trader.DiaryDay`, optional: День из дневника.
        """

        try:
            for i, lesson in enumerate(data['lessons']):
                data['lessons'][i] = DiaryLesson.de_json(lesson)
        except KeyError:
            data['lessons'] = []

        data = super(DiaryDay, cls).de_json(data)

        return cls(**data)
