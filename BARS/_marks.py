from dataclasses import dataclass
from collections.abc import Sequence

from ._base import ClientObject

@dataclass
class Mark(ClientObject):
    """Класс, представляющий данные оценки.

    Attributes:
        date (:obj:`str`): Дата формата Год-Месяц-День.
        description (:obj:`str`): Описание оценки.
        mark (:obj:`int`): Оценка.
    """

    date: str
    description: str
    mark: int

    @classmethod
    def de_json(
            cls: dataclass,
            data: dict,
    ) -> 'Mark':
        """Десериализация объекта.

        Args:
            data (:obj:`dict`): Поля и значения десериализуемого объекта.

        Returns:
            :class:`BARS.Mark`: Данные оценки.
        """

        data['mark'] = int(data['mark'])

        data = super(Mark, cls).de_json(data)

        return cls(**data)

@dataclass
class SummaryMarksDiscipline(ClientObject):
    """Класс, представляющий данные урока из сводной.

    Attributes:
        average_mark (:obj:`float`): Средняя оценка.
        discipline (:obj:`str`): Название урока.
        marks (Sequence[:class:`BARS.Mark`]): Оценки урока.
    """

    average_mark: float
    discipline: str
    marks: Sequence['Mark']

    @classmethod
    def de_json(
            cls: dataclass,
            data: dict,
    ) -> 'SummaryMarksDiscipline':
        """Десериализация объекта.

        Args:
            data (:obj:`dict`): Поля и значения десериализуемого объекта.

        Returns:
            :class:`BARS.SummaryMarksDiscipline`: Данные урока из сводной.
        """

        data['average_mark'] = float(data['average_mark'])

        for i, mark in enumerate(data['marks']):
            data['marks'][i] = Mark.de_json(mark)

        data = super(SummaryMarksDiscipline, cls).de_json(data)

        return cls(**data)

@dataclass
class Subperiod(ClientObject):
    """Класс, представляющий информацию о четверти.

    Attributes:
        code (:obj:`str`): Кодовое название четверти.
        name (:obj:`str`): Название четверти.
    """

    code: str
    name: str

    @classmethod
    def de_json(
            cls: dataclass,
            data: dict,
    ) -> 'Subperiod':
        """Десериализация объекта.

        Args:
            data (:obj:`dict`): Поля и значения десериализуемого объекта.

        Returns:
            :class:`steam_trader.Subperiod`, optional: Информация о четверти.
        """

        data = super(Subperiod, cls).de_json(data)

        return cls(**data)

@dataclass
class SummaryMarks(ClientObject):
    """Класс, представляющий данные о сводных оценках.

    Attributes:
        dates (Sequence[:obj:`str`]): Даты из сводной.
        disciplines (Sequence[:class:`BARS.SummaryMarksDiscipline`]): Последовательность уроков из сводной.
        subperiod (:class:`BARS.Subperiod`): Информация о четверти.
    """

    dates: Sequence[str]
    disciplines: Sequence['SummaryMarksDiscipline']
    subperiod: Subperiod

    @classmethod
    def de_json(
            cls: dataclass,
            data: dict,
    ) -> 'SummaryMarks':
        """Десериализация объекта.

        Args:
            data (:obj:`dict`): Поля и значения десериализуемого объекта.

        Returns:
            :class:`steam_trader.DiaryLesson`, optional: Урок из дневника.
        """

        data['disciplines'] = data['discipline_marks']
        del data['discipline_marks']

        for i, item in enumerate(data['disciplines']):
            data['disciplines'][i] = SummaryMarksDiscipline.de_json(item)

        data['subperiod'] = Subperiod.de_json(data['subperiod'])

        data = super(SummaryMarks, cls).de_json(data)

        return cls(**data)

@dataclass
class TotalMarksDiscipline(ClientObject):
    """Класс, представляющий данные урока из сводной.

    Attributes:
        discipline (:obj:`str`): Название урока.
        period_marks (Sequence[:class:`BARS.Mark`]): Последовательность оценок в четвертях.
    """

    discipline: str
    period_marks: Sequence[int]

    @classmethod
    def de_json(
            cls: dataclass,
            data: dict,
    ) -> 'TotalMarksDiscipline':
        """Десериализация объекта.

        Args:
            data (:obj:`dict`): Поля и значения десериализуемого объекта.

        Returns:
            :class:`BARS.TotalMarksDiscipline`: Данные урока из сводной.
        """

        for i, mark in enumerate(data['period_marks']):
            data['period_marks'][i] = int(data['period_marks'][i])

        data = super(TotalMarksDiscipline, cls).de_json(data)

        return cls(**data)

@dataclass
class TotalMarks(ClientObject):
    """Класс, представляющий информацию об итоговых оценках.

    Attributes:
        disciplines (Sequence[:class:`TotalMarksDiscipline`]): Последовательность соответствующих предметов
        subperiods (Sequence[:class:`Subperiod`]): Последовательность четвертей
    """

    disciplines: Sequence['TotalMarksDiscipline']
    subperiods: Sequence['Subperiod']

    @classmethod
    def de_json(
            cls: dataclass,
            data: dict,
    ) -> 'TotalMarks':
        """Десериализация объекта.

        Args:
            data (:obj:`dict`): Поля и значения десериализуемого объекта.

        Returns:
            :class:`steam_trader.Subperiod`, optional: Информация о четверти.
        """

        data['disciplines'] = data['discipline_marks']
        del data['discipline_marks']

        for i, mark in enumerate(data['disciplines']):
            data['disciplines'][i] = TotalMarksDiscipline.de_json(mark)

        for i, subperiod in enumerate(data['subperiods']):
            data['subperiods'][i] = Subperiod.de_json(subperiod)

        data = super(TotalMarks, cls).de_json(data)

        return cls(**data)

@dataclass
class AttendaceData(ClientObject):
    """Класс, представляющий отсчёт о посещаемиости.

    Attributes:
        absent (:obj:`int`): Всего отсутствовал.
        absent_bad (:obj:`int`): Отсутствовал без уважительной причины.
        absent_good (:obj:`int`): Отсутствовал по уважительной причине.
        ill (:obj:`int`): Отсутствовал по болезни.
        present (:obj:`int`): % Присутствия.
        total (:obj:`int`): Всего %.
    """

    absent: int
    absent_bad: int
    absent_good: int
    ill: int
    present: int
    total: int

    @classmethod
    def de_json(
            cls: dataclass,
            data: dict,
    ) -> 'AttendaceData':
        """Десериализация объекта.

        Args:
            data (:obj:`dict`): Поля и значения десериализуемого объекта.

        Returns:
            :class:`BARS.AttendaceData`: Отсчёт о посещаемости.
        """

        data = super(AttendaceData, cls).de_json(data)

        return cls(**data)

@dataclass
class SeriesItem(ClientObject):
    """Класс, представляющий график оценок.

    Attributes:
        color (:obj:`str`): HEX код цвета.
        data (Sequence[:obj:`int`]): Оценки на графике. Среднее арифметическое.
        name (:obj:`str`): Название пункта.
        point_width (:obj:`str`): Ширина точки в пикселях.
    """

    color: str
    data: Sequence[int]
    name: str
    point_width: str

    @classmethod
    def de_json(
            cls: dataclass,
            data: dict,
    ) -> 'SeriesItem':
        """Десериализация объекта.

        Args:
            data (:obj:`dict`): Поля и значения десериализуемого объекта.

        Returns:
            :class:`BARS.SeriesItem`: График оценок.
        """

        data['point_width'] = data['pointWidth']
        del data['pointWidth']

        data = super(SeriesItem, cls).de_json(data)

        return cls(**data)

@dataclass
class ProgressData(ClientObject):
    """Класс, представляющий данные об успеваемости.

    Attributes:
        categories (Sequence[:obj:`int`]): Неизвестно.
        dates (Sequence[:obj:`str`]): Даты с оценками.
        series (Sequence[:class:`BARS.SeriesItem`]): Данные графика.
        subject (:obj:`str`): Название предмета.
    """

    categories: Sequence[int]
    dates: Sequence[str]
    series: Sequence['SeriesItem']
    subject: str

    @classmethod
    def de_json(
            cls: dataclass,
            data: dict,
    ) -> 'ProgressData':
        """Десериализация объекта.

        Args:
            data (:obj:`dict`): Поля и значения десериализуемого объекта.

        Returns:
            :class:`BARS.ProgressData`: Данные об успеваемости.
        """

        for i, item in enumerate(data['series']):
            data['series'][i] = SeriesItem.de_json(item)

        data = super(ProgressData, cls).de_json(data)

        return cls(**data)
