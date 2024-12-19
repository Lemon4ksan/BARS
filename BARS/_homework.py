from dataclasses import dataclass
from collections.abc import Sequence

from ._base import ClientObject

@dataclass(slots=True)
class HomeworkLesson(ClientObject):
    """Класс, представляющий урок из домашнего задания.

    Attributes:
        date (`str`): Дата формата День-Месяц-Год.
        discipline (`str`): Название урока.
        homework (`str`): Домашнее задание.
        homework_time_to_complete (`int`): Время на выполнения д/з.
        individual_homeworks (Sequence[`str`]): Индивидуальные задания.
        materials (Sequence[`str`]): Неабсолютные ссылки на прикреплённые файлы.
        next_individual_homeworks (Sequence[`str`]): Индивидуальные задания на следующий урок.
        next_materials (Sequence[`str`]): Неабсолютные ссылки на прикреплённые файлы на следующий урок.
        next_homework_time_to_complete (`int`): Время на выполнения д/з на следующий урок.
        schedulelessontype (`str`): Вид работы.
        teacher (`str`): Учитель, проводящий урок.
        theme (`str`): Тема урока.
    """

    date: str
    discipline: str
    homework: str
    homework_time_to_complete: int
    individual_homeworks: Sequence[str]
    materials: Sequence[dict[str, str]]
    next_homework: str
    next_individual_homeworks: Sequence[str]
    next_materials: Sequence[str]
    next_homework_time_to_complete: int
    schedulelessontype: str
    teacher: str
    theme: str

    @classmethod
    def de_json(
            cls,
            data: dict,
    ) -> 'HomeworkLesson':

        data.update({
            'individual_homeworks': data['individualHomeworks'],
            'next_homework': data['nextHomework'],
            'next_individual_homeworks': data['nextIndividualHomeworks'],
            'next_materials': data['nextMaterials']
        })
        del data['individualHomeworks'], data['nextHomework'], data['nextIndividualHomeworks'], data['nextMaterials']
        # TODO: Это надо добавить

        data = super(HomeworkLesson, cls).de_json(data)

        return cls(**data)

@dataclass(slots=True)
class HomeworkDay(ClientObject):
    """Класс, представляющий день из дневника.

    Attributes:
        date (`str`): Дата формата Год-Месяц-День.
        homeworks (Sequence[`BARS.HomeworkLesson`]): Д/З на этот день.
        name (`str`): Название дня недели.
    """

    date: str
    homeworks: Sequence[HomeworkLesson]
    name: str

    @classmethod
    def de_json(
            cls,
            data: dict,
    ) -> 'HomeworkDay':

        for i, homework in enumerate(data['homeworks']):
            data['homeworks'][i] = HomeworkLesson.de_json(homework)

        data = super(HomeworkDay, cls).de_json(data)

        return cls(**data)
