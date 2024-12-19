from dataclasses import dataclass
from collections.abc import Sequence

from ._base import ClientObject

@dataclass(slots=True)
class UnlockedDiscilpine(ClientObject):
    """Класс, представляющий доступную дисциплину.

    Attributes:
        id (`int`): Уникальный идентификатор дисциплины.
        name (`str`): Название дисциплины.
    """

    id: int
    name: str

    @classmethod
    def de_json(
            cls,
            data: dict,
    ) -> 'UnlockedDiscilpine':

        data = super(UnlockedDiscilpine, cls).de_json(data)

        return cls(**data)

@dataclass(slots=True)
class AccountInfo(ClientObject):
    """Класс, представляющий информацию об аккаунте.

    Attributes:
        charts_urls (`dict`): Неизвестно.
        disciplines (Sequence[`BARS.UnlockedDiscilpine`]): Доступные предметы.
        period_begin (`str`): Начало текущей четверт форамата Год-Месяц-День.
        period_end (`str`): Конец текущей четверти форамата Год-Месяц-День.
        pupilid (`int`): Идентификатор ученика.
        student_id_param_name (`str`): Неизвестно.
    """

    charts_urls: dict
    disciplines: Sequence[UnlockedDiscilpine]
    period_begin: str
    period_end: str
    pupilid: int
    student_id_param_name: str

    @classmethod
    def de_json(
            cls,
            data: dict,
    ) -> 'AccountInfo':

        data['pupilid'] = data['pupil_id']
        del data['pupil_id']

        for i, discipline in enumerate(data['disciplines']):
            data['disciplines'][i] = UnlockedDiscilpine.de_json(discipline)

        data = super(AccountInfo, cls).de_json(data)

        return cls(**data)

@dataclass(slots=True)
class PupilInfo(ClientObject):
    """Класс, представляющий информацию об ученике.

    Attributes:
        auth_user_profile_id (`int`): ID аторизованного пользователя.
        children_persons (Sequence[`int`]): Последовательность ID детей (если вы родитель).
        indicators (Sequence[`dict`]): Последовательность со словарями индикаторов итоговых оценок.
        selected_pupil_ava_url (`str`): Неабсолютная ссылка на изображение выбранного пользователя.
        selected_pupil_classyear (`str`): Учебный год выбранного ученика.
        selected_pupil_classyear (`int`): ID выбранного ученика.
        selected_pupil_is_male (`bool`): Является ли выбранный ученик мужчиной.
        selected_pupil_name (`str`): Имя выбранного ученика.
        selected_pupil_school (`str`): Школа выбранного ученика.
        user_ava_url (`str`): Неабсолютная ссылка на изображение профиля.
        user_desc (`str`): Описание пользователя.
        user_fullname (`str`): ФИО пользователя.
        user_ava_url (`bool`): Есть ли у пользователя изображение профиля.
        user_is_male (`bool`): Является ли пользователь мужчиной.
    """

    auth_user_profile_id: int
    children_persons: Sequence[int]
    indicators: Sequence[dict]
    selected_pupil_ava_url: str
    selected_pupil_classyear: str
    selected_pupil_id: int
    selected_pupil_is_male: bool
    selected_pupil_name: str
    selected_pupil_school: str
    user_ava_url: str
    user_desc: str
    user_fullname: str
    user_has_ava: bool
    user_is_male: bool

    @classmethod
    def de_json(
            cls,
            data: dict,
    ) -> 'PupilInfo':

        data = super(PupilInfo, cls).de_json(data)

        return cls(**data)
