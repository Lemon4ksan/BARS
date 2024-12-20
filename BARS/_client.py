import json
import httpx
import logging
import functools
from collections.abc import Sequence, Callable
from typing import Optional, Literal, Any, Self, Type
from types import TracebackType

from .exceptions import Unauthorized, BClientException, InternalError
from ._base import ClientObject
from ._diary import DiaryDay
from ._schedule import ScheduleDay, ScheduleMonth
from ._marks import SummaryMarks, TotalMarks, AttendaceData, ProgressData
from ._account import AccountInfo, PupilInfo
from ._school import SchoolInfo, ClassInfo
from ._homework import HomeworkDay
from ._misc import Event, Birthday


logging.getLogger(__name__).addHandler(logging.NullHandler())

def log(method: Callable[..., Any]) -> Any:
    logger = logging.getLogger(method.__module__)

    @functools.wraps(method)
    def wrapper(*args, **kwargs) -> Any:
        logger.debug(f'Entering: {method.__name__}')

        result = method(*args, **kwargs)
        logger.info(result)

        logger.debug(f'Exiting: {method.__name__}')

        return result

    return wrapper


class BClient(ClientObject):
    """Класс, представляющий клиент для оращение к БАРСу.

    Args:
        sessionid (`str`): Идентификатор вашей сессии. Данный способ обращения является костылём, но способа лучше не было найдено.
            Можно найти в файлах куки с помощью DevTools.
        proxy (`str`, optional): Прокси для запросов. Для работы необходимо использовать контекстный менеджер with.
        base_url (`str`, optional): Ссылка на домен сайта.
        headers (`dict`, optional): Словарь, содержащий сведения об устройстве, с которого выполняются запросы.
            Используется при каждом запросе на сайт.

    Attributes:
        sessionid (`str`): Идентификатор вашей сессии.
        proxy (`str`, optional): Прокси для запросов.
        base_url (`str`, optional): Ссылка на домен сайта.
        headers (`dict`, optional): Словарь, содержащий сведения об устройстве, с которого выполняются запросы.
            Используется при каждом запросе на сайт.
    """

    def __init__(
            self,
            sessionid: str,
            *,
            proxy: Optional[str] = None,
            base_url: Optional[str] = None,
            headers: Optional[dict] = None) -> None:

        self.sessionid = sessionid

        if base_url is None:
            base_url = "https://xn--80atdl2c.xn--33-6kcadhwnl3cfdx.xn--p1ai/"
        self.base_url = base_url

        if headers is None:
            headers = {
                'user-agent': 'python3',
                'wrapper': 'BARS-Public-API',
                'manufacturer': 'Lemon4ksan',
            }
        self.headers = headers

        self._httpx_client: Optional[httpx.Client] = None
        self.proxy = proxy

    def __enter__(self) -> Self:
        self._httpx_client = httpx.Client(proxy=self.proxy)
        return self

    def __exit__(
        self,
        t: Optional[Type[BaseException]],
        value: Optional[BaseException],
        traceback: Optional[TracebackType]
    ) -> None:
        if self._httpx_client:
            self._httpx_client.close()

    @log
    def get_diary(self, date: str) -> Sequence[DiaryDay]:
        """Получить данные из вкладки 'Дневник'.

        Args:
            date (`str`): Дата формата Год-Месяц-День, неделя которой будет возвращена.

        Returns:
            Sequence[`BARS.DiaryDay`]: Неделя из дневника.
        """

        url = self.base_url + 'api/ScheduleService/GetDiary'
        try:
            result = (self._httpx_client or httpx).get(
                url,
                headers=self.headers,
                params={'date': date, 'is_diary': True},
                cookies={'sessionid': self.sessionid}
            ).json()
        except json.JSONDecodeError:
            raise InternalError('В данный момент сайт недоступен.')

        if isinstance(result, dict) and 'faultcode' in result:
            match result['faultcode']:
                case 'Server.UserNotAuthenticated':
                    raise Unauthorized('Недействительный sessionid')
                case _:
                    raise BClientException(f'Неизвестная ошибка :: {result['faultcode']}: {result['faultstring']}')

        return [DiaryDay.de_json(day) for day in result['days']]

    @log
    def get_week_schedule(self, date: str) -> Sequence[ScheduleDay]:
        """Получить данные из вкладки 'Расписание > Неделя'.

        Args:
            date (`str`): Дата формата Год-Месяц-День, неделя которой будет возвращена.

        Returns:
            Sequence[`BARS.DiaryDay`]: Расписание на неделю.
        """

        url = self.base_url + 'api/ScheduleService/GetWeekSchedule'
        try:
            result = (self._httpx_client or httpx).get(
                url,
                headers=self.headers,
                params={'date': date},
                cookies={'sessionid': self.sessionid}
            ).json()
        except json.JSONDecodeError:
            raise InternalError('В данный момент сайт недоступен.')

        if isinstance(result, dict) and 'faultcode' in result:
            match result['faultcode']:
                case 'Server.UserNotAuthenticated':
                    raise Unauthorized('Недействительный sessionid')
                case _:
                    raise BClientException(f'Неизвестная ошибка :: {result['faultcode']}: {result['faultstring']}')

        return_data = []
        for day in result['days']:
            return_data.append(ScheduleDay.de_json(day))
        return return_data

    @log
    def get_month_schedule(self, date: str) -> Sequence[ScheduleMonth]:
        """Получить данные из вкладки 'Расписание > Месяц'.

        Args:
            date (`str`): Дата формата Год-Месяц-День, неделя которой будет возвращена.

        Returns:
            Sequence[`BARS.ScheduleMonth`]: Расписание на месяц.
        """

        url = self.base_url + 'api/ScheduleService/GetMonthSchedule'
        try:
            result = (self._httpx_client or httpx).get(
                url,
                headers=self.headers,
                params={'date': date},
                cookies={'sessionid': self.sessionid}
            ).json()
        except json.JSONDecodeError:
            raise InternalError('В данный момент сайт недоступен.')

        if isinstance(result, dict) and 'faultcode' in result:
            match result['faultcode']:
                case 'Server.UserNotAuthenticated':
                    raise Unauthorized('Недействительный sessionid')
                case _:
                    raise BClientException(f'Неизвестная ошибка :: {result['faultcode']}: {result['faultstring']}')

        return_data = []
        for month in result:
            return_data.append(ScheduleMonth.de_json(month))
        return return_data

    @log
    def get_schedule_report_link(self, date: str, interval: Literal['week', 'month'] = 'week') -> str:
        """Поулчить абсолютную ссылку на загрузку таблицы расписания.

        Args:
            date (`str`): Дата формата Год-Месяц-День, неделя которой будет возвращена.
            interval (`LiteralString`): Интервал расписания.
                'week' - Неделя (по умолчанию).
                'month' - Месяц.

        Returns:
            `str`: Абсолютная ссылка на загрузку таблицы расписания.
        """

        url = self.base_url + 'api/ScheduleService/ScheduleReport'
        try:
            result = (self._httpx_client or httpx).get(
                url,
                headers=self.headers,
                params={'date': date, 'interval': interval},
                cookies={'sessionid': self.sessionid}
            ).json()
        except json.JSONDecodeError:
            raise InternalError('В данный момент сайт недоступен.')

        if isinstance(result, dict) and 'faultcode' in result:
            match result['faultcode']:
                case 'Server.UserNotAuthenticated':
                    raise Unauthorized('Недействительный sessionid')
                case _:
                    raise BClientException(f'Неизвестная ошибка :: {result['faultcode']}: {result['faultstring']}')
        elif isinstance(result, str):
            return 'https://xn--80atdl2c.xn--33-6kcadhwnl3cfdx.xn--p1ai' + result.replace('"', "")
        else:
            raise ValueError(f"Был получен непредусмотренный тип '{type(result).__name__}' вместо ожидаемого 'dict' или 'str'.")

    @log
    def get_summary_marks(self, date: str) -> SummaryMarks:
        """Поулчить данные из вкладки 'Оценки > Сводная'.

        Args:
            date (`str`): Дата формата Год-Месяц-День, четверть которой будет возвращена.

        Returns:
            `BARS.SummaryMarks`: Сводные оценки.
        """

        url = self.base_url + 'api/MarkService/GetSummaryMarks'
        try:
            result = (self._httpx_client or httpx).get(
                url,
                headers=self.headers,
                params={'date': date},
                cookies={'sessionid': self.sessionid}
            ).json()
        except json.JSONDecodeError:
            raise InternalError('В данный момент сайт недоступен.')

        if 'faultcode' in result:
            match result['faultcode']:
                case 'Server.UserNotAuthenticated':
                    raise Unauthorized('Недействительный sessionid')
                case _:
                    raise BClientException(f'Неизвестная ошибка :: {result['faultcode']}: {result['faultstring']}')

        return SummaryMarks.de_json(result)

    @log
    def get_total_marks(self) -> TotalMarks:
        """Поулчить данные из вкладки 'Оценки > Итоговые'. Данные ограничены этим годом.

        Returns:
            `BARS.SummaryMarks`: Итоговые оценки.
        """

        url = self.base_url + 'api/MarkService/GetTotalMarks'
        try:
            result = (self._httpx_client or httpx).get(
                url,
                headers=self.headers,
                cookies={'sessionid': self.sessionid}
            ).json()
        except json.JSONDecodeError:
            raise InternalError('В данный момент сайт недоступен.')

        if 'faultcode' in result:
            match result['faultcode']:
                case 'Server.UserNotAuthenticated':
                    raise Unauthorized('Недействительный sessionid')
                case _:
                    raise BClientException(f'Неизвестная ошибка :: {result['faultcode']}: {result['faultstring']}')

        return TotalMarks.de_json(result)

    @log
    def get_account_info(self) -> AccountInfo:
        """Получить скрытую информацию об аккаунте. Реализуется через GetVisualizationData.

        Returns:
            `BARS.AccountInfo`: Информация об аккаунте.
        """

        url = self.base_url + 'api/MarkService/GetVisualizationData'
        try:
            result = (self._httpx_client or httpx).get(
                url,
                headers=self.headers,
                cookies={'sessionid': self.sessionid}
            ).json()
        except json.JSONDecodeError:
            raise InternalError('В данный момент сайт недоступен.')

        if 'faultcode' in result:
            match result['faultcode']:
                case 'Server.UserNotAuthenticated':
                    raise Unauthorized('Недействительный sessionid')
                case _:
                    raise BClientException(f'Неизвестная ошибка :: {result['faultcode']}: {result['faultstring']}')

        return AccountInfo.de_json(result)

    @log
    def get_pupil_info(self) -> PupilInfo:
        """Получить данные об ученике.

        Returns:
            `BARS.PupilInfo`: Информация об ученике.
        """

        url = self.base_url + 'api/ProfileService/GetPersonData'
        try:
            result = (self._httpx_client or httpx).get(
                url,
                headers=self.headers,
                cookies={'sessionid': self.sessionid}
            ).json()
        except json.JSONDecodeError:
            raise InternalError('В данный момент сайт недоступен.')

        if 'faultcode' in result:
            match result['faultcode']:
                case 'Server.UserNotAuthenticated':
                    raise Unauthorized('Недействительный sessionid')
                case _:
                    raise BClientException(f'Неизвестная ошибка :: {result['faultcode']}: {result['faultstring']}')

        return PupilInfo.de_json(result)

    @log
    def get_attendace_data(self, pupilid: int, date_begin: str, date_end: str, subjectid: int = 0) -> AttendaceData:
        """Получить данные о посещаемости.

        Для получения данных аргументов См. get_account_info.

        Args:
            pupilid (`int`): Уникальный идентификатор ученика.
            date_begin (`int`): Год-Месяц-День, начала отсчёта.
            date_end (`int`): Год-Месяц-День, конца отсчёта.
            subjectid (`int`): Уникальный идентификатор предмета. 0 - общая статистика.

        Returns:
            `BARS.AttendanceData`: Данные о посещаемости.
        """

        url = self.base_url + 'actions/web_edu.core.pupil.chart.ChartPack/attendancedata'
        try:
            result = httpx.post(
                url,
                headers=self.headers,
                data={
                    'web_edu.plugins.corrective_school.corrective_card.actions.StudentPack_id': pupilid,
                    'subject': subjectid,
                    'date_begin': date_begin,
                    'date_end': date_end
                },
                cookies={'sessionid': self.sessionid}
            ).json()
        except json.JSONDecodeError:
            raise InternalError('В данный момент сайт недоступен.')

        if 'faultcode' in result:
            match result['faultcode']:
                case 'Server.UserNotAuthenticated':
                    raise Unauthorized('Недействительный sessionid')
                case _:
                    raise BClientException(f'Неизвестная ошибка :: {result['faultcode']}: {result['faultstring']}')

        return AttendaceData.de_json(result)

    @log
    def get_progress_data(self, pupilid: int, date_begin: str, date_end: str, subjectid: int = 0) -> ProgressData:
        """Получить данные об успеваемости.

        Для получения данных аргументов См. get_account_info.

        Args:
            pupilid (`int`): Уникальный идентификатор ученика.
            date_begin (`int`): Год-Месяц-День, начала отсчёта.
            date_end (`int`): Год-Месяц-День, конца отсчёта.
            subjectid (`int`): Уникальный идентификатор предмета. 0 - общая статистика.

        Returns:
            `ProgressData`: Данные об успеваемости.
        """

        url = self.base_url + 'actions/web_edu.core.pupil.chart.ChartPack/progressdata'
        try:
            result = httpx.post(
                url,
                headers=self.headers,
                data={
                    'web_edu.plugins.corrective_school.corrective_card.actions.StudentPack_id': pupilid,
                    'subject': subjectid,
                    'date_begin': date_begin,
                    'date_end': date_end
                },
                cookies={'sessionid': self.sessionid}
            ).json()
        except json.JSONDecodeError:
            raise InternalError('В данный момент сайт недоступен.')

        if 'faultcode' in result:
            match result['faultcode']:
                case 'Server.UserNotAuthenticated':
                    raise Unauthorized('Недействительный sessionid')
                case _:
                    raise BClientException(f'Неизвестная ошибка :: {result['faultcode']}: {result['faultstring']}')

        return ProgressData.de_json(result)

    @log
    def get_school_info(self) -> SchoolInfo:
        """Получить информацию об учебном заведении.

        Returns:
            `BARS.SchoolInfo`: Информация о школе.
        """

        url = self.base_url + 'api/SchoolService/getSchoolInfo'
        try:
            result = (self._httpx_client or httpx).get(
                url,
                headers=self.headers,
                cookies={'sessionid': self.sessionid}
            ).json()
        except json.JSONDecodeError:
            raise InternalError('В данный момент сайт недоступен.')

        if 'faultcode' in result:
            match result['faultcode']:
                case 'Server.UserNotAuthenticated':
                    raise Unauthorized('Недействительный sessionid')
                case _:
                    raise BClientException(f'Неизвестная ошибка :: {result['faultcode']}: {result['faultstring']}')

        return SchoolInfo.de_json(result)

    @log
    def get_class_info(self) -> ClassInfo:
        """Получить информацию о классе.

        Returns:
            `BARS.ClassInfo`: Информация о классе.
        """

        url = self.base_url + 'api/SchoolService/getClassYearInfo'
        try:
            result = (self._httpx_client or httpx).get(
                url,
                headers=self.headers,
                cookies={'sessionid': self.sessionid}
            ).json()
        except json.JSONDecodeError:
            raise InternalError('В данный момент сайт недоступен.')

        if 'faultcode' in result:
            match result['faultcode']:
                case 'Server.UserNotAuthenticated':
                    raise Unauthorized('Недействительный sessionid')
                case _:
                    raise BClientException(f'Неизвестная ошибка :: {result['faultcode']}: {result['faultstring']}')

        return ClassInfo.de_json(result)

    @log
    def get_homework(self, date: str) -> Sequence[HomeworkDay]:
        """Получить данные из вкладки 'Домашнее задание'.

        Args:
            date (`str`): Дата формата Год-Месяц-День, неделя которой будет возвращена.

        Returns:
            Sequence[`BARS.HomeworkDay`]: Неделя домашнего задания.
        """

        url = self.base_url + 'api/HomeworkService/GetHomeworkFromRange'
        try:
            result = (self._httpx_client or httpx).get(
                url,
                headers=self.headers,
                params={'date': date, 'is_diary': True},
                cookies={'sessionid': self.sessionid}
            ).json()
        except json.JSONDecodeError:
            raise InternalError('В данный момент сайт недоступен.')

        if isinstance(result, dict) and 'faultcode' in result:
            match result['faultcode']:
                case 'Server.UserNotAuthenticated':
                    raise Unauthorized('Недействительный sessionid')
                case _:
                    raise BClientException(f'Неизвестная ошибка :: {result['faultcode']}: {result['faultstring']}')
        elif isinstance(result, list):
            for i, birthday in enumerate(result):
                result[i] = Birthday.de_json(birthday)
            return result
        else:
            return []

    @log
    def get_birthdays(self) -> Optional[Sequence[Birthday]]:
        """Получить список текущих дней рождений.

        Returns:
            Sequence[`BARS.Birthday`], optional: Список текущих дней рождений. None если нет.
        """

        url = self.base_url + 'api/WidgetService/getBirthdays'
        try:
            result = (self._httpx_client or httpx).get(
                url,
                headers=self.headers,
                cookies={'sessionid': self.sessionid}
            ).json()
        except json.JSONDecodeError:
            raise InternalError('В данный момент сайт недоступен.')

        if isinstance(result, dict) and 'faultcode' in result:
            match result['faultcode']:
                case 'Server.UserNotAuthenticated':
                    raise Unauthorized('Недействительный sessionid')
                case _:
                    raise BClientException(f'Неизвестная ошибка :: {result['faultcode']}: {result['faultstring']}')
        elif isinstance(result, list):
            for i, birthday in enumerate(result):
                result[i] = Birthday.de_json(birthday)
            return result
        else:
            return []

    @log
    def get_events(self) -> Sequence[Event]:
        """Получить список текущих праздников.

        Returns:
            Sequence[`BARS.Event`], optional: Список текущих праздников. None если нет.
        """

        url = self.base_url + 'api/WidgetService/getEvents'
        try:
            result = (self._httpx_client or httpx).get(
                url,
                headers=self.headers,
                cookies={'sessionid': self.sessionid}
            ).json()
        except json.JSONDecodeError:
            raise InternalError('В данный момент сайт недоступен.')

        if isinstance(result, dict) and 'faultcode' in result:
            match result['faultcode']:
                case 'Server.UserNotAuthenticated':
                    raise Unauthorized('Недействительный sessionid')
                case _:
                    raise BClientException(f'Неизвестная ошибка :: {result['faultcode']}: {result['faultstring']}')
        elif isinstance(result, list):
            for i, event in enumerate(result):
                result[i] = Event.de_json(event)
            return result
        else:
            return []
