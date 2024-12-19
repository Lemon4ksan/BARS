from dataclasses import dataclass
from collections.abc import Sequence

from ._base import ClientObject

@dataclass(slots=True)
class Mark(ClientObject):
    """Класс, представляющий данные оценки.

    Attributes:
        date (`str`): Дата формата Год-Месяц-День.
        description (`str`): Описание оценки.
        mark (`int`): Оценка.
    """

    date: str
    description: str
    mark: int

    @classmethod
    def de_json(
            cls,
            data: dict,
    ) -> 'Mark':

        data['mark'] = int(data['mark'])

        data = super(Mark, cls).de_json(data)

        return cls(**data)

@dataclass(slots=True)
class SummaryMarksDiscipline(ClientObject):
    """Класс, представляющий данные урока из сводной.

    Attributes:
        average_mark (`float`): Средняя оценка.
        discipline (`str`): Название урока.
        marks (Sequence[`BARS.Mark`]): Оценки урока.
    """

    average_mark: float
    discipline: str
    marks: Sequence[Mark]

    @classmethod
    def de_json(
            cls,
            data: dict,
    ) -> 'SummaryMarksDiscipline':

        data['average_mark'] = float(data['average_mark'])

        for i, mark in enumerate(data['marks']):
            data['marks'][i] = Mark.de_json(mark)

        data = super(SummaryMarksDiscipline, cls).de_json(data)

        return cls(**data)

@dataclass(slots=True)
class Subperiod(ClientObject):
    """Класс, представляющий информацию о четверти.

    Attributes:
        code (`str`): Кодовое название четверти.
        name (`str`): Название четверти.
    """

    code: str
    name: str

    @classmethod
    def de_json(
            cls,
            data: dict,
    ) -> 'Subperiod':

        data = super(Subperiod, cls).de_json(data)

        return cls(**data)

@dataclass(slots=True)
class SummaryMarks(ClientObject):
    """Класс, представляющий данные о сводных оценках.

    Attributes:
        dates (Sequence[`str`]): Даты из сводной.
        disciplines (Sequence[`BARS.SummaryMarksDiscipline`]): Последовательность уроков из сводной.
        subperiod (`BARS.Subperiod`): Информация о четверти.
    """

    dates: Sequence[str]
    disciplines: Sequence[SummaryMarksDiscipline]
    subperiod: Subperiod

    @classmethod
    def de_json(
            cls,
            data: dict,
    ) -> 'SummaryMarks':

        data['disciplines'] = data['discipline_marks']
        del data['discipline_marks']

        for i, item in enumerate(data['disciplines']):
            data['disciplines'][i] = SummaryMarksDiscipline.de_json(item)

        data['subperiod'] = Subperiod.de_json(data['subperiod'])

        data = super(SummaryMarks, cls).de_json(data)

        return cls(**data)

@dataclass(slots=True)
class TotalMarksDiscipline(ClientObject):
    """Класс, представляющий данные урока из сводной.

    Attributes:
        discipline (`str`): Название урока.
        period_marks (Sequence[`dict[str, str]`]): Последовательность словарей оценок в четвертях. Ключ 'mark' - оценка, ключ 'subperiod_code' - код четверти.
    """

    discipline: str
    period_marks: Sequence[dict[str, str]]

    @classmethod
    def de_json(
            cls,
            data: dict,
    ) -> 'TotalMarksDiscipline':

        data = super(TotalMarksDiscipline, cls).de_json(data)

        return cls(**data)

@dataclass(slots=True)
class TotalMarks(ClientObject):
    """Класс, представляющий информацию об итоговых оценках.

    Attributes:
        disciplines (Sequence[`TotalMarksDiscipline`]): Последовательность соответствующих предметов
        subperiods (Sequence[`Subperiod`]): Последовательность четвертей
    """

    disciplines: Sequence[TotalMarksDiscipline]
    subperiods: Sequence[Subperiod]

    @classmethod
    def de_json(
            cls,
            data: dict,
    ) -> 'TotalMarks':

        data['disciplines'] = data['discipline_marks']
        del data['discipline_marks']

        for i, mark in enumerate(data['disciplines']):
            data['disciplines'][i] = TotalMarksDiscipline.de_json(mark)

        for i, subperiod in enumerate(data['subperiods']):
            data['subperiods'][i] = Subperiod.de_json(subperiod)

        data = super(TotalMarks, cls).de_json(data)

        return cls(**data)

@dataclass(slots=True)
class AttendaceData(ClientObject):
    """Класс, представляющий отсчёт о посещаемиости. Данные измеряются в уроках.

    Attributes:
        absent (`int`): Всего отсутствовал.
        absent_bad (`int`): Отсутствовал без уважительной причины.
        absent_good (`int`): Отсутствовал по уважительной причине.
        ill (`int`): Отсутствовал по болезни.
        present (`int`): Присутствовал.
        total (`int`): Всего.
    """

    absent: int
    absent_bad: int
    absent_good: int
    ill: int
    present: int
    total: int

    @classmethod
    def de_json(
            cls,
            data: dict,
    ) -> 'AttendaceData':

        data = super(AttendaceData, cls).de_json(data)

        return cls(**data)

@dataclass(slots=True)
class SeriesItem(ClientObject):
    """Класс, представляющий график оценок.

    Attributes:
        color (`str`): HEX код цвета.
        data (Sequence[`int`]): Оценки на графике. Среднее арифметическое.
        name (`str`): Название пункта.
        point_width (`str`): Ширина точки в пикселях.
    """

    color: str
    data: Sequence[int]
    name: str
    point_width: str

    @classmethod
    def de_json(
            cls,
            data: dict,
    ) -> 'SeriesItem':

        data['point_width'] = data['pointWidth']
        del data['pointWidth']

        data = super(SeriesItem, cls).de_json(data)

        return cls(**data)

@dataclass(slots=True)
class ProgressData(ClientObject):
    """Класс, представляющий данные об успеваемости.

    Attributes:
        categories (Sequence[`int`]): Неизвестно.
        dates (Sequence[`str`]): Даты с оценками.
        series (Sequence[`BARS.SeriesItem`]): Данные графика.
        subject (`str`): Название предмета.
    """

    categories: Sequence[int]
    dates: Sequence[str]
    series: Sequence[SeriesItem]
    subject: str

    @classmethod
    def de_json(
            cls,
            data: dict,
    ) -> 'ProgressData':

        for i, item in enumerate(data['series']):
            data['series'][i] = SeriesItem.de_json(item)

        data = super(ProgressData, cls).de_json(data)

        return cls(**data)
