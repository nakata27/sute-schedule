"""
Schedule Fetcher - получение расписания с сайта MIA КНУТЭ
"""

import requests
from typing import Optional, Dict, Any
from bs4 import BeautifulSoup
import time
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class ScheduleFetcherError(Exception):
    """Базовая ошибка Fetcher"""
    pass


class RateLimitError(ScheduleFetcherError):
    """Превышен лимит запросов"""
    pass


class ScheduleFetcher:
    """
    Класс для получения расписания с сайта MIA
    Реализует rate limiting и retry механизмы
    """

    BASE_URL = "https://mia1.knute.edu.ua"
    SCHEDULE_URL = f"{BASE_URL}/time-table/group"

    def __init__(
        self,
        rate_limit_delay: float = 1.0,
        max_retries: int = 3,
        timeout: int = 10
    ):
        """
        Args:
            rate_limit_delay: Задержка между запросами (в секундах)
            max_retries: Максимальное количество попыток
            timeout: Таймаут запроса (в секундах)
        """
        self.rate_limit_delay = rate_limit_delay
        self.max_retries = max_retries
        self.timeout = timeout
        self.last_request_time = 0.0
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'MIA Schedule App/1.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'uk,en;q=0.9',
        })

    def _wait_for_rate_limit(self):
        """Ожидание для соблюдения rate limit"""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time

        if time_since_last_request < self.rate_limit_delay:
            sleep_time = self.rate_limit_delay - time_since_last_request
            logger.debug(f"Rate limit: sleeping for {sleep_time:.2f}s")
            time.sleep(sleep_time)

        self.last_request_time = time.time()

    def _get_csrf_token(self) -> Optional[str]:
        """
        Получает CSRF токен с главной страницы

        Returns:
            CSRF токен или None
        """
        try:
            self._wait_for_rate_limit()
            response = self.session.get(self.SCHEDULE_URL, timeout=self.timeout)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')
            csrf_input = soup.find('input', {'name': '_csrf-frontend'})

            if csrf_input:
                token = csrf_input.get('value')
                logger.debug(f"CSRF token obtained: {token[:20]}...")
                return token

            logger.warning("CSRF token not found in page")
            return None

        except Exception as e:
            logger.error(f"Error getting CSRF token: {e}")
            return None

    def fetch_schedule(
        self,
        group_id: str,
        faculty_id: str,
        course: str,
        retry_count: int = 0
    ) -> Optional[str]:
        """
        Получает HTML расписания для указанной группы

        Args:
            group_id: ID группы
            faculty_id: ID факультета
            course: Курс
            retry_count: Текущая попытка (для рекурсии)

        Returns:
            HTML содержимое страницы с расписанием или None

        Raises:
            ScheduleFetcherError: При критической ошибке
            RateLimitError: При превышении лимита запросов
        """
        try:
            # Получаем CSRF токен
            csrf_token = self._get_csrf_token()
            if not csrf_token:
                raise ScheduleFetcherError("Failed to obtain CSRF token")

            # Подготавливаем данные формы
            form_data = {
                '_csrf-frontend': csrf_token,
                'TimeTableForm[facultyId]': faculty_id,
                'TimeTableForm[course]': course,
                'TimeTableForm[groupId]': group_id
            }

            logger.info(f"Fetching schedule for group {group_id}, faculty {faculty_id}, course {course}")

            # Ждем rate limit
            self._wait_for_rate_limit()

            # Отправляем POST запрос
            response = self.session.post(
                f"{self.SCHEDULE_URL}?type=0",
                data=form_data,
                timeout=self.timeout
            )

            # Проверяем статус
            if response.status_code == 429:
                logger.warning("Rate limit exceeded (429)")
                raise RateLimitError("Rate limit exceeded")

            response.raise_for_status()

            # Проверяем, что получили валидный HTML
            if len(response.text) < 1000:
                logger.warning("Response too short, might be an error")
                raise ScheduleFetcherError("Invalid response received")

            logger.info(f"Successfully fetched schedule ({len(response.text)} bytes)")
            return response.text

        except RateLimitError:
            if retry_count < self.max_retries:
                wait_time = (retry_count + 1) * self.rate_limit_delay * 2
                logger.info(f"Retrying in {wait_time}s (attempt {retry_count + 1}/{self.max_retries})")
                time.sleep(wait_time)
                return self.fetch_schedule(group_id, faculty_id, course, retry_count + 1)
            else:
                logger.error("Max retries exceeded")
                raise

        except requests.RequestException as e:
            if retry_count < self.max_retries:
                logger.warning(f"Request failed: {e}. Retrying... (attempt {retry_count + 1}/{self.max_retries})")
                time.sleep(self.rate_limit_delay)
                return self.fetch_schedule(group_id, faculty_id, course, retry_count + 1)
            else:
                logger.error(f"Request failed after {self.max_retries} retries: {e}")
                raise ScheduleFetcherError(f"Failed to fetch schedule: {e}")

        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise ScheduleFetcherError(f"Unexpected error: {e}")

    def close(self):
        """Закрывает сессию"""
        self.session.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

