from dataclasses import dataclass
from collections.abc import Sequence

from ._base import ClientObject

@dataclass(slots=True)
class Employee(ClientObject):
    """Класс, представляющий данные работника учебного заведения.

    Attributes:
        group (`str`): Группа
        fullname (`str`): ФИО.
        category (`str`): Категория.
        employer_jobs (Sequence[`str`]): Список работ.
        male (`bool`): Является ли работник мужчиной.
        photo (`str`): Неабсолютная ссылка на прикреплённое фото.
    """

    group: str
    fullname: str
    category: str
    employer_jobs: Sequence[str]
    male: bool
    photo: str

    @classmethod
    def de_json(
            cls,
            data: dict,
    ) -> 'Employee':

        data = super(Employee, cls).de_json(data)

        return cls(**data)

@dataclass(slots=True)
class SchoolInfo(ClientObject):
    """Класс, представляющий данные об учебном заведении.

    Attributes:
        name (`str`): Название.
        address (`str`): Адрес.
        phone (`str`): Номер телефона.
        site_url (`str`): Абсолютная ссылка на сайт школы.
        count_employees (`int`): Кол-во рабочего персонала.
        count_pupils (`int`): Кол-во учашихся.
        photo (`str`): Неабсолютная ссылка на прикреплённое фото.
        email (`str`): Электронная почта.
        ustav (`str`): Неабсолютная ссылка на устав УЗ.
        employees (Sequence[`BARS.Employee`]): Рабочий персонал.
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
    employees: Sequence[Employee]

    @classmethod
    def de_json(
            cls,
            data: dict,
    ) -> 'SchoolInfo':

        for i, employee in enumerate(data['employees']):
            data['employees'][i] = Employee.de_json(employee)

        data = super(SchoolInfo, cls).de_json(data)

        return cls(**data)

@dataclass(slots=True)
class Pupil(ClientObject):
    """Класс, представляющий данные ученика.

    Attributes:
        fullname (`str`): ФИО.
        photo (`str`): Неабсолютная ссылка на прикреплённое изображение.
        male (`bool`): Является ли ученик мужиной.
    """

    fullname: str
    male: bool
    photo: str

    @classmethod
    def de_json(
            cls,
            data: dict,
    ) -> 'Pupil':

        data = super(Pupil, cls).de_json(data)

        return cls(**data)

@dataclass(slots=True)
class ClassInfo(ClientObject):
    """Класс, представляющий данные о классе.

    Attributes:
        study_level (`int`): Цифра класса.
        letter (`str`): Буква класса.
        form_master (`str`): ФИО классного руководителя
        form_master_photo (`str`): Неабсолютная ссылка на прикреплённое изображение классного руководителя.
        form_master_male (`bool`): Является ли классный руководитель мужчиной.
        specialization (`str`): Направление класса.
        photo (`str`): Неабсолютная ссылка на прикреплённое изображение класса.
        pupils (Sequence[`BARS.Pupil`]): Ученики.
    """

    study_level: int
    letter: str
    form_master: str
    form_master_photo: str
    form_master_male: bool
    specialization: str
    photo: str
    pupils: Sequence[Pupil]

    @classmethod
    def de_json(
            cls,
            data: dict,
    ) -> 'ClassInfo':

        for i, pupil in enumerate(data['pupils']):
            data['pupils'][i] = Pupil.de_json(pupil)

        data = super(ClassInfo, cls).de_json(data)

        return cls(**data)
