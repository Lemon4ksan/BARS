from dataclasses import dataclass
from collections.abc import Sequence

from ._base import ClientObject

@dataclass
class Employee(ClientObject):
    """Класс, представляющий данные работника учебного заведения.

    Attributes:
        group (:obj:`str`): Группа
        fullname (:obj:`str`): ФИО.
        category (:obj:`str`): Категория.
        employer_jobs (Sequence[:obj:`str`]): Список работ.
        male (:obj:`bool`): Является ли работник мужчиной.
        photo (:obj:`str`): Неабсолютная ссылка на прикреплённое фото.
    """

    group: str
    fullname: str
    category: str
    employer_jobs: Sequence[str]
    male: bool
    photo: str

    @classmethod
    def de_json(
            cls: dataclass,
            data: dict,
    ) -> 'Employee':
        """Десериализация объекта.

        Args:
            data (:obj:`dict`): Поля и значения десериализуемого объекта.

        Returns:
            :class:`BARS.Employee`: Данные работника.
        """

        data = super(Employee, cls).de_json(data)

        return cls(**data)

@dataclass
class SchoolInfo(ClientObject):
    """Класс, представляющий данные об учебном заведении.

    Attributes:
        name (:obj:`str`): Название.
        address (:obj:`str`): Адрес.
        phone (:obj:`str`): Номер телефона.
        site_url (:obj:`str`): Абсолютная ссылка на сайт школы.
        count_employees (:obj:`int`): Кол-во рабочего персонала.
        count_pupils (:obj:`int`): Кол-во учашихся.
        photo (:obj:`str`): Неабсолютная ссылка на прикреплённое фото.
        email (:obj:`str`): Электронная почта.
        ustav (:obj:`str`): Неабсолютная ссылка на устав УЗ.
        employees (Sequence[:class:`BARS.Employee`]): Рабочий персонал.
    """

    name: str
    address: str
    phone: str
    site_url: str
    count_employees: int
    count_pupils: int
    photo: str
    email: str
    ustav: str
    employees: Sequence['Employee']

    @classmethod
    def de_json(
            cls: dataclass,
            data: dict,
    ) -> 'SchoolInfo':
        """Десериализация объекта.

        Args:
            data (:obj:`dict`): Поля и значения десериализуемого объекта.

        Returns:
            :class:`BARS.SchoolInfo`: Данный об учебном заведении.
        """

        for i, employee in enumerate(data['employees']):
            data['employees'][i] = Employee.de_json(employee)

        data = super(SchoolInfo, cls).de_json(data)

        return cls(**data)

@dataclass
class Pupil(ClientObject):
    """Класс, представляющий данные ученика.

    Attributes:
        fullname (:obj:`str`): ФИО.
        photo (:obj:`str`): Неабсолютная ссылка на прикреплённое изображение.
        male (:obj:`bool`): Является ли ученик мужиной.
    """

    fullname: str
    male: bool
    photo: str

    @classmethod
    def de_json(
            cls: dataclass,
            data: dict,
    ) -> 'Pupil':
        """Десериализация объекта.

        Args:
            data (:obj:`dict`): Поля и значения десериализуемого объекта.

        Returns:
            :class:`BARS.Pupil`: Данные ученика.
        """

        data = super(Pupil, cls).de_json(data)

        return cls(**data)

@dataclass
class ClassInfo(ClientObject):
    """Класс, представляющий данные о классе.

    Attributes:
        study_level (:obj:`int`): Цифра класса.
        letter (:obj:`str`): Буква класса.
        form_master (:obj:`str`): ФИО классного руководителя
        form_master_photo (:obj:`str`): Неабсолютная ссылка на прикреплённое изображение классного руководителя.
        form_master_male (:obj:`bool`): Является ли классный руководитель мужчиной.
        specialization (:obj:`str`): Направление класса.
        photo (:obj:`str`): Неабсолютная ссылка на прикреплённое изображение класса.
        pupils (Sequence[:class:`BARS.Pupil`]): Ученики.
    """

    study_level: int
    letter: str
    form_master: str
    form_master_photo: str
    form_master_male: bool
    specialization: str
    photo: str
    pupils: Sequence['Pupil']

    @classmethod
    def de_json(
            cls: dataclass,
            data: dict,
    ) -> 'ClassInfo':
        """Десериализация объекта.

        Args:
            data (:obj:`dict`): Поля и значения десериализуемого объекта.

        Returns:
            :class:`BARS.ClassInfo`: Данный о классе.
        """

        for i, pupil in enumerate(data['pupils']):
            data['pupils'][i] = Pupil.de_json(pupil)

        data = super(ClassInfo, cls).de_json(data)

        return cls(**data)
