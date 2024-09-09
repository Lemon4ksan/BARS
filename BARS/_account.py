from dataclasses import dataclass
from collections.abc import Sequence

from ._base import ClientObject

@dataclass
class UnlockedDiscilpine(ClientObject):
    """Класс, представляющий доступную дисциплину.

    Attributes:
        id (:obj:`int`): Уникальный идентификатор дисциплины.
        name (:obj:`str`): Название дисциплины.
    """

    id: int
    name: str

    @classmethod
    def de_json(
            cls: dataclass,
            data: dict,
    ) -> 'UnlockedDiscilpine':
        """Десериализация объекта.

        Args:
            data (:obj:`dict`): Поля и значения десериализуемого объекта.

        Returns:
            :class:`BARS.Mark`: Доступная дисциплина.
        """

        data = super(UnlockedDiscilpine, cls).de_json(data)

        return cls(**data)

@dataclass
class AccountInfo(ClientObject):
    """Класс, представляющий информацию об аккаунте.

    charts_urls (:obj:`dict`): Неизвестно.
    disciplines (Sequence[:class:`BARS.UnlockedDiscilpine`]): Доступные предметы.
    period_begin (:obj:`str`): Начало текущей четверт форамата Год-Месяц-День.
    period_end (:obj:`str`): Конец текущей четверти форамата Год-Месяц-День.
    pupilid (:obj:`int`): Идентификатор ученика.
    student_id_param_name (:obj:`str`): Неизвестно.
    """

    charts_urls: dict
    disciplines: Sequence['UnlockedDiscilpine']
    period_begin: str
    period_end: str
    pupilid: int
    student_id_param_name: str

    @classmethod
    def de_json(
            cls: dataclass,
            data: dict,
    ) -> 'AccountInfo':
        """Десериализация объекта.

        Args:
            data (:obj:`dict`): Поля и значения десериализуемого объекта.

        Returns:
            :class:`BARS.AccountInfo`: Информация об аккаунте.
        """

        data['pupilid'] = data['pupil_id']
        del data['pupil_id']

        for i, discipline in enumerate(data['disciplines']):
            data['disciplines'][i] = UnlockedDiscilpine.de_json(discipline)

        data = super(AccountInfo, cls).de_json(data)

        return cls(**data)

@dataclass
class PupilInfo(ClientObject):
    """Класс, представляющий информацию об ученике.

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
            cls: dataclass,
            data: dict,
    ) -> 'PupilInfo':
        """Десериализация объекта.

        Args:
            data (:obj:`dict`): Поля и значения десериализуемого объекта.

        Returns:
            :class:`BARS.PupilInfo`: Информация об ученике.
        """

        data = super(PupilInfo, cls).de_json(data)

        return cls(**data)
