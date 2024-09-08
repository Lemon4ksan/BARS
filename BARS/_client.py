import httpx
import logging
import functools
from collections.abc import Sequence, Callable
from typing import Optional, LiteralString, TypeVar, Any

from ._base import ClientObject
from ._diary import DiaryDay
from ._schedule import DaySchedule, MonthSchedule
from ._marks import SummaryMarks, TotalMarks, AttendaceData, ProgressData
from ._account import AccountInfo
from ._school import SchoolInfo, ClassInfo
from ._homework import HomeworkDay
from .exceptions import Unauthorized, BClientException


F = TypeVar('F', bound=Callable[..., Any])

def log(method: F) -> F:
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
        sessionid (:obj:`str`): Идентификатор вашей сессии. Данный способ обращения является костылём, но способа лучше не было найдено.
            Можно найти в файлах куки с помощью DevTools.
        proxy (:obj:`str`, optional): Прокси для запросов. Для работы необходимо использовать контекстный менеджер with.
        base_url (:obj:`str`, optional): Ссылка на домен сайта.
        headers (:obj:`dict`, optional): Словарь, содержащий сведения об устройстве, с которого выполняются запросы.
            Используется при каждом запросе на сайт.

    Attributes:
        sessionid (:obj:`str`): Идентификатор вашей сессии.
        proxy (:obj:`str`, optional): Прокси для запросов.
        base_url (:obj:`str`, optional): Ссылка на домен сайта.
        headers (:obj:`dict`, optional): Словарь, содержащий сведения об устройстве, с которого выполняются запросы.
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

        self._httpx_client = None
        self.proxy = proxy

    def __enter__(self):
        self._httpx_client = httpx.Client(proxy=self.proxy)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._httpx_client.close()

    @log
    def get_diary(self, date: str) -> Sequence['DiaryDay']:
        """Получить данные из вкладки 'Дневник'.

        Args:
            date (:obj:`str`): Дата формата Год-Месяц-День, неделя которой будет возвращена.

        Returns:
            Sequence[:obj:`BARS.DiaryDay`]: Неделя из дневника.
        """

        url = self.base_url + 'api/ScheduleService/GetDiary'
        result = httpx.get(
            url,
            headers=self.headers,
            params={'date': date, 'is_diary': True},
            cookies={'sessionid': self.sessionid}
        ).json()

        if isinstance(result, dict) and 'faultcode' in result.keys():
            match result['faultcode']:
                case 'Server.UserNotAuthenticated':
                    raise Unauthorized('Недействительный sessionid')
                case _:
                    raise BClientException(f'Неизвестная ошибка :: {result['faultcode']}: {result['faultstring']}')

        return_data = []
        for day in result['days']:
            return_data.append(DiaryDay.de_json(day))
        return return_data

    @log
    def get_week_schedule(self, date: str) -> Sequence['DaySchedule']:
        """Получить данные из вкладки 'Расписание > Неделя'.

        Args:
            date (:obj:`str`): Дата формата Год-Месяц-День, неделя которой будет возвращена.

        Returns:
            Sequence[:obj:`BARS.DiaryDay`]: Расписание на неделю.
        """

        url = self.base_url + 'api/ScheduleService/GetWeekSchedule'
        result = httpx.get(
            url,
            headers=self.headers,
            params={'date': date},
            cookies={'sessionid': self.sessionid}
        ).json()

        if isinstance(result, dict) and 'faultcode' in result.keys():
            match result['faultcode']:
                case 'Server.UserNotAuthenticated':
                    raise Unauthorized('Недействительный sessionid')
                case _:
                    raise BClientException(f'Неизвестная ошибка :: {result['faultcode']}: {result['faultstring']}')

        return_data = []
        for day in result['days']:
            return_data.append(DaySchedule.de_json(day))
        return return_data

    @log
    def get_month_schedule(self, date: str) -> Sequence['MonthSchedule']:
        """Получить данные из вкладки 'Расписание > Месяц'.

        Args:
            date (:obj:`str`): Дата формата Год-Месяц-День, неделя которой будет возвращена.

        Returns:
            Sequence[:obj:`BARS.MonthSchedule`]: Расписание на месяц.
        """

        url = self.base_url + 'api/ScheduleService/GetMonthSchedule'
        result = httpx.get(
            url,
            headers=self.headers,
            params={'date': date},
            cookies={'sessionid': self.sessionid}
        ).json()

        if isinstance(result, dict) and 'faultcode' in result.keys():
            match result['faultcode']:
                case 'Server.UserNotAuthenticated':
                    raise Unauthorized('Недействительный sessionid')
                case _:
                    raise BClientException(f'Неизвестная ошибка :: {result['faultcode']}: {result['faultstring']}')

        return_data = []
        for month in result:
            return_data.append(MonthSchedule.de_json(month))
        return return_data

    @log
    def get_schedule_report_link(self, date: str, interval: LiteralString = 'week') -> str:
        """Поулчить абсолютную ссылку на загрузку таблицы расписания.

        Args:
            date (:obj:`str`): Дата формата Год-Месяц-День, неделя которой будет возвращена.
            interval (:obj:`LiteralString`): Интервал расписания.
                'week' - Неделя (по умолчанию).
                'month' - Месяц.

        Returns:
            :obj:`str`: Абсолютная ссылка на загрузку таблицы расписания.
        """

        url = self.base_url + 'api/ScheduleService/ScheduleReport'
        result = httpx.get(
            url,
            headers=self.headers,
            params={'date': date, 'interval': interval},
            cookies={'sessionid': self.sessionid}
        ).json()

        if isinstance(result, dict) and 'faultcode' in result.keys():
            match result['faultcode']:
                case 'Server.UserNotAuthenticated':
                    raise Unauthorized('Недействительный sessionid')
                case _:
                    raise BClientException(f'Неизвестная ошибка :: {result['faultcode']}: {result['faultstring']}')

        return 'https://xn--80atdl2c.xn--33-6kcadhwnl3cfdx.xn--p1ai' + result.replace('"', "")

    @log
    def get_summary_marks(self, date: str) -> 'SummaryMarks':
        """Поулчить данные из вкладки 'Оценки > Сводная'.

        Args:
            date (:obj:`str`): Дата формата Год-Месяц-День, четверть которой будет возвращена.

        Returns:
            :class:`BARS.SummaryMarks`: Сводные оценки.
        """

        url = self.base_url + 'api/MarkService/GetSummaryMarks'
        result = httpx.get(
            url,
            headers=self.headers,
            params={'date': date},
            cookies={'sessionid': self.sessionid}
        ).json()

        if 'faultcode' in result.keys():
            match result['faultcode']:
                case 'Server.UserNotAuthenticated':
                    raise Unauthorized('Недействительный sessionid')
                case _:
                    raise BClientException(f'Неизвестная ошибка :: {result['faultcode']}: {result['faultstring']}')

        return SummaryMarks.de_json(result)

    @log
    def get_total_marks(self) -> 'TotalMarks':
        """Поулчить данные из вкладки 'Оценки > Итоговые'. Данные ограничены этим годом.

        Returns:
            :class:`BARS.SummaryMarks`: Итоговые оценки.
        """

        url = self.base_url + 'api/MarkService/GetTotalMarks'
        result = httpx.get(
            url,
            headers=self.headers,
            cookies={'sessionid': self.sessionid}
        ).json()

        if 'faultcode' in result.keys():
            match result['faultcode']:
                case 'Server.UserNotAuthenticated':
                    raise Unauthorized('Недействительный sessionid')
                case _:
                    raise BClientException(f'Неизвестная ошибка :: {result['faultcode']}: {result['faultstring']}')

        return TotalMarks.de_json(result)

    @log
    def get_account_info(self) -> 'AccountInfo':
        """Получить скрытую информацию об аккаунте. Реализуется через GetVisualizationData.

        Returns:
            :class:`BARS.AccountInfo`: Информация об аккаунте.
        """

        url = self.base_url + 'api/MarkService/GetVisualizationData'
        result = httpx.get(
            url,
            headers=self.headers,
            cookies={'sessionid': self.sessionid}
        ).json()

        if 'faultcode' in result.keys():
            match result['faultcode']:
                case 'Server.UserNotAuthenticated':
                    raise Unauthorized('Недействительный sessionid')
                case _:
                    raise BClientException(f'Неизвестная ошибка :: {result['faultcode']}: {result['faultstring']}')

        return AccountInfo.de_json(result)

    @log
    def get_attendace_data(self, pupilid: int, date_begin: str, date_end: str, subjectid: int = 0) -> 'AttendaceData':
        """Получить данные о посещаемости.

        Для получения данных аргументов См. get_account_info.

        Args:
            pupilid (:obj:`int`): Уникальный идентификатор ученика.
            date_begin (:obj:`int`): Год-Месяц-День, начала отсчёта.
            date_end (:obj:`int`): Год-Месяц-День, конца отсчёта.
            subjectid (:obj:`int`): Уникальный идентификатор предмета. 0 - общая статистика.

        Returns:
            :class:`BARS.AttendanceData`: Данные о посещаемости.
        """

        url = self.base_url + 'actions/web_edu.core.pupil.chart.ChartPack/attendancedata'
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

        if 'faultcode' in result.keys():
            match result['faultcode']:
                case 'Server.UserNotAuthenticated':
                    raise Unauthorized('Недействительный sessionid')
                case _:
                    raise BClientException(f'Неизвестная ошибка :: {result['faultcode']}: {result['faultstring']}')

        return AttendaceData.de_json(result)

    @log
    def get_progress_data(self, pupilid: int, date_begin: str, date_end: str, subjectid: int = 0) -> 'ProgressData':
        """Получить данные об успеваемости.

        Для получения данных аргументов См. get_account_info.

        Args:
            pupilid (:obj:`int`): Уникальный идентификатор ученика.
            date_begin (:obj:`int`): Год-Месяц-День, начала отсчёта.
            date_end (:obj:`int`): Год-Месяц-День, конца отсчёта.
            subjectid (:obj:`int`): Уникальный идентификатор предмета. 0 - общая статистика.

        Returns:
            :class:`ProgressData`: Данные об успеваемости.
        """

        url = self.base_url + 'actions/web_edu.core.pupil.chart.ChartPack/progressdata'
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

        if 'faultcode' in result.keys():
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
            :class:`BARS.SchoolInfo`: Информация о школе.
        """

        url = self.base_url + 'api/SchoolService/getSchoolInfo'
        result = httpx.get(
            url,
            headers=self.headers,
            cookies={'sessionid': self.sessionid}
        ).json()

        if 'faultcode' in result.keys():
            match result['faultcode']:
                case 'Server.UserNotAuthenticated':
                    raise Unauthorized('Недействительный sessionid')
                case _:
                    raise BClientException(f'Неизвестная ошибка :: {result['faultcode']}: {result['faultstring']}')

        return SchoolInfo.de_json(result)

    @log
    def get_class_info(self):
        """Получить информацию о классе.

        Returns:
            :class:`BARS.ClassInfo`: Информация о классе.
        """

        url = self.base_url + 'api/SchoolService/getClassYearInfo'
        result = httpx.get(
            url,
            headers=self.headers,
            cookies={'sessionid': self.sessionid}
        ).json()

        if 'faultcode' in result.keys():
            match result['faultcode']:
                case 'Server.UserNotAuthenticated':
                    raise Unauthorized('Недействительный sessionid')
                case _:
                    raise BClientException(f'Неизвестная ошибка :: {result['faultcode']}: {result['faultstring']}')

        return ClassInfo.de_json(result)

    @log
    def get_homework(self, date: str) -> Sequence['HomeworkDay']:
        """Получить данные из вкладки 'Домашнее задание'.

        Args:
            date (:obj:`str`): Дата формата Год-Месяц-День, неделя которой будет возвращена.

        Returns:
            Sequence[:obj:`BARS.DiaryDay`]: Неделя домашнего задания.
        """

        url = self.base_url + 'api/HomeworkService/GetHomeworkFromRange'
        result = httpx.get(
            url,
            headers=self.headers,
            params={'date': date, 'is_diary': True},
            cookies={'sessionid': self.sessionid}
        ).json()

        if isinstance(result, dict) and 'faultcode' in result.keys():
            match result['faultcode']:
                case 'Server.UserNotAuthenticated':
                    raise Unauthorized('Недействительный sessionid')
                case _:
                    raise BClientException(f'Неизвестная ошибка :: {result['faultcode']}: {result['faultstring']}')

        for i, day in enumerate(result):
            result[i] = HomeworkDay.de_json(day)
        return result
