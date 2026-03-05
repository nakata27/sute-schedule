"""Schedule parser — converts timetable HTML into structured data models."""

from bs4 import BeautifulSoup
from typing import List, Optional, Dict, Any
from datetime import datetime, date
import re
import logging

from ..models.schedule import (
    Lesson,
    LessonType,
    DaySchedule,
    WeekSchedule,
    GroupInfo,
    ScheduleResponse
)

logger = logging.getLogger(__name__)


class ScheduleParserError(Exception):
    """Ошибка парсинга"""
    pass


class ScheduleParser:
    """
    Парсер HTML расписания с сайта MIA
    """

    # Маппинг CSS классов на типы занятий
    LESSON_TYPE_CLASSES = {
        'lesson-1': LessonType.LECTURE,      # Лекция - желтый
        'lesson-2': LessonType.PRACTICE,     # Практика - зеленый
        'lesson-3': LessonType.SESSION,      # Сессия - красный
        'lesson-4': LessonType.EXAM,         # Экзамен
        'lesson-5': LessonType.CONSULTATION, # Консультация
    }

    # Стандартное время пар
    DEFAULT_LESSON_TIMES = {
        1: ("08:20", "09:40"),
        2: ("10:05", "11:25"),
        3: ("12:05", "13:25"),
        4: ("13:50", "15:10"),
        5: ("15:20", "16:40"),
        6: ("16:50", "18:10"),
        7: ("18:20", "19:40"),
    }

    def __init__(self):
        self.soup: Optional[BeautifulSoup] = None

    def parse(
        self,
        html: str,
        group_info: GroupInfo
    ) -> ScheduleResponse:
        """
        Парсит HTML расписания

        Args:
            html: HTML содержимое страницы
            group_info: Информация о группе

        Returns:
            Структурированное расписание
        """
        self.soup = BeautifulSoup(html, 'html.parser')

        # Находим таблицу расписания
        table = self.soup.find('table', {'id': 'timeTable'})
        if not table:
            raise ScheduleParserError("Schedule table not found")

        # Парсим недели
        weeks = self._parse_weeks(table)

        logger.info(f"Parsed {len(weeks)} weeks with schedule")

        return ScheduleResponse(
            group_info=group_info,
            weeks=weeks,
            fetched_at=datetime.now()
        )

    def _parse_weeks(self, table) -> List[WeekSchedule]:
        """Парсит недели из таблицы"""
        weeks = []
        week_dates = self._extract_week_dates(table)

        if not week_dates:
            logger.warning("No week dates found")
            return weeks

        # Создаем словарь для хранения данных по неделям
        weeks_data: Dict[int, Dict[date, DaySchedule]] = {}

        for week_idx in range(len(week_dates[0])):
            weeks_data[week_idx] = {}

        # Парсим строки таблицы
        rows = table.find_all('tr')
        current_day_dates = []
        current_lesson_info = None

        for row in rows:
            # Проверяем, это строка с днем недели?
            day_header = row.find('th', class_='headday')
            if day_header:
                # Извлекаем даты для этого дня
                date_headers = row.find_all('th', class_='headdate')
                current_day_dates = []

                for date_header in date_headers:
                    date_text = date_header.get_text(strip=True)
                    parsed_date = self._parse_date(date_text)
                    if parsed_date:
                        current_day_dates.append(parsed_date)

                continue

            # Проверяем, это строка с информацией о паре?
            lesson_header = row.find('th', class_='headcol')
            if lesson_header and current_day_dates:
                # Извлекаем номер пары и время
                lesson_number = self._extract_lesson_number(lesson_header)
                start_time, end_time = self._extract_lesson_time(lesson_header)

                current_lesson_info = {
                    'lesson_number': lesson_number,
                    'start_time': start_time,
                    'end_time': end_time
                }

                # Парсим ячейки с занятиями
                cells = row.find_all('td')

                for week_idx, cell in enumerate(cells):
                    if week_idx >= len(current_day_dates):
                        break

                    lesson_date = current_day_dates[week_idx]

                    # Пропускаем закрытые ячейки
                    if 'closed' in cell.get('class', []):
                        continue

                    # Парсим содержимое ячейки
                    lessons = self._parse_cell(cell, lesson_date, current_lesson_info)

                    # Добавляем занятия в расписание
                    if lessons:
                        if lesson_date not in weeks_data[week_idx]:
                            weeks_data[week_idx][lesson_date] = DaySchedule(
                                day_date=lesson_date,
                                day_of_week=lesson_date.weekday(),
                                lessons=[]
                            )

                        weeks_data[week_idx][lesson_date].lessons.extend(lessons)

        # Формируем объекты WeekSchedule
        for week_idx, days_dict in weeks_data.items():
            if not days_dict:
                continue

            dates = sorted(days_dict.keys())
            if not dates:
                continue

            week_start = dates[0]
            week_end = dates[-1]

            # Сортируем дни
            days = [days_dict[d] for d in dates]

            week = WeekSchedule(
                week_number=week_idx + 1,
                week_start=week_start,
                week_end=week_end,
                days=days
            )
            weeks.append(week)

        return weeks

    def _extract_week_dates(self, table) -> List[List[date]]:
        """Извлекает даты недель из заголовков таблицы"""
        week_dates = []

        date_rows = table.find_all('tr')
        for row in date_rows:
            date_headers = row.find_all('th', class_='headdate')
            if date_headers:
                dates = []
                for header in date_headers:
                    date_text = header.get_text(strip=True)
                    parsed_date = self._parse_date(date_text)
                    if parsed_date:
                        dates.append(parsed_date)

                if dates:
                    week_dates.append(dates)

        return week_dates

    def _parse_date(self, date_text: str) -> Optional[date]:
        """Парсит дату из текста формата DD.MM.YYYY"""
        try:
            return datetime.strptime(date_text.strip(), '%d.%m.%Y').date()
        except ValueError:
            logger.debug(f"Failed to parse date: {date_text}")
            return None

    def _extract_lesson_number(self, header) -> int:
        """Извлекает номер пары из заголовка"""
        lesson_span = header.find('span', class_='lesson')
        if lesson_span:
            text = lesson_span.get_text(strip=True)
            match = re.search(r'(\d+)', text)
            if match:
                return int(match.group(1))
        return 1

    def _extract_lesson_time(self, header) -> tuple[str, str]:
        """Извлекает время пары из заголовка"""
        start_span = header.find('span', class_='start')
        end_span = header.find('span', class_='end')

        start_time = start_span.get_text(strip=True) if start_span else "00:00"
        end_time = end_span.get_text(strip=True) if end_span else "00:00"

        return start_time, end_time

    def _parse_cell(
        self,
        cell,
        lesson_date: date,
        lesson_info: Dict[str, Any]
    ) -> List[Lesson]:
        """Парсит ячейку с занятием"""
        lessons = []

        # Ищем блоки с занятиями
        lesson_divs = cell.find_all('div', class_=lambda x: x and any(
            cls in x for cls in ['lesson-1', 'lesson-2', 'lesson-3', 'lesson-4', 'lesson-5']
        ))

        for lesson_div in lesson_divs:
            # Определяем тип занятия по классу
            lesson_type = LessonType.UNKNOWN
            for class_name in lesson_div.get('class', []):
                if class_name in self.LESSON_TYPE_CLASSES:
                    lesson_type = self.LESSON_TYPE_CLASSES[class_name]
                    break

            # Ищем основной div с информацией
            info_div = lesson_div.find('div', {'data-toggle': 'popover'})
            if not info_div:
                continue

            # Извлекаем данные из data-content (полная информация)
            data_content = info_div.get('data-content', '')
            subject, room, teacher_full, announcement = self._parse_data_content(data_content)

            # Ищем кнопку объявления (если есть)
            ads_button = lesson_div.find('a', class_='btn-show-ads')
            if ads_button and not announcement:
                # Берем ID объявления из data-r1
                ads_id = ads_button.get('data-r1')
                ads_date = ads_button.get('data-r2')
                if ads_id and ads_date:
                    # Сохраняем ID объявления для последующей загрузки через XHR
                    announcement = f"ads:{ads_id}"

            # Извлекаем видимый текст (сокращенная версия)
            visible_text = info_div.get_text(separator='\n', strip=True)

            # Извлекаем преподавателя из видимого текста
            teacher = self._extract_teacher_short(visible_text)

            # Определяем тип из текста, если не удалось по классу
            if lesson_type == LessonType.UNKNOWN:
                lesson_type = self._detect_lesson_type(visible_text)

            # Создаем объект Lesson
            lesson = Lesson(
                lesson_number=lesson_info['lesson_number'],
                start_time=lesson_info['start_time'],
                end_time=lesson_info['end_time'],
                lesson_date=lesson_date,
                subject=subject or self._clean_subject(visible_text),
                lesson_type=lesson_type,
                room=room,
                teacher=teacher,
                teacher_full=teacher_full,
                announcement=announcement,
                raw_html=str(lesson_div)
            )

            lessons.append(lesson)

        return lessons

    def _parse_data_content(self, data_content: str) -> tuple[Optional[str], Optional[str], Optional[str], Optional[str]]:
        """Парсит data-content атрибут, возвращает (subject, room, teacher_full, announcement)"""
        if not data_content:
            return None, None, None, None

        # Убираем HTML теги
        clean_content = re.sub(r'<br\s*/?>', '\n', data_content)
        clean_content = re.sub(r'<[^>]+>', '', clean_content)

        lines = [line.strip() for line in clean_content.split('\n') if line.strip()]

        subject = None
        room = None
        teacher_full = None
        announcement = None

        if not lines:
            return None, None, None, None

        # Строка 1: Предмет[Тип]
        subject_line = lines[0]
        subject = re.sub(r'\[.*?\]', '', subject_line).strip()
        subject = subject.strip('"').strip('"В"').strip()

        # Строка 2: ауд. ...
        if len(lines) > 1:
            room_line = lines[1]
            if 'ауд' in room_line.lower():
                room = room_line.replace('ауд.', '').replace('ауд', '').strip()

        # Ищем объявление
        # Ключевые слова для поиска объявлений
        announcement_keywords = ['оголошення', 'увага', 'важливо', 'примітка', 'note', 'announcement']
        announcement_found = False

        for i, line in enumerate(lines):
            line_lower = line.lower()
            # Проверяем есть ли ключевое слово в строке
            for keyword in announcement_keywords:
                if keyword in line_lower:
                    announcement_lines = []

                    # Если в строке есть текст после ключевого слова, берем его
                    # Например: "Оголошення: текст объявления"
                    if ':' in line:
                        parts = line.split(':', 1)
                        if len(parts) > 1 and parts[1].strip():
                            announcement_lines.append(parts[1].strip())

                    # Берем все последующие строки до "Додано"
                    for j in range(i + 1, len(lines)):
                        if 'додано' in lines[j].lower():
                            break
                        # Пропускаем пустые строки и строки с другими данными
                        if lines[j].strip() and not any(x in lines[j] for x in ['ФТБ', 'ФІТ', 'МТП', 'ауд']):
                            announcement_lines.append(lines[j])

                    if announcement_lines:
                        announcement = ' '.join(announcement_lines)
                        announcement_found = True
                    break

            if announcement_found:
                break

        # ПРЕПОДАВАТЕЛЬ - это последняя строка перед "Додано"
        # Структура: [0]=Предмет, [1]=Аудитория, [2]=Группа, [3]=ПРЕПОДАВАТЕЛЬ, [4]=Додано
        # Идем с конца, находим "Додано", берем строку перед ней
        dodano_index = -1
        for i in range(len(lines) - 1, -1, -1):
            if 'додано' in lines[i].lower():
                dodano_index = i
                break

        if dodano_index > 2:  # Должно быть минимум: предмет, аудитория, что-то, преподаватель
            # Берем строку перед "Додано"
            potential_teacher = lines[dodano_index - 1]

            # Проверяем что это не группа, не предмет, не аудитория, не объявление
            is_group = any(x in potential_teacher for x in ['ФТБ', 'ФІТ', 'МТП', 'ФМК', 'ФЕБ', 'ФРМ', 'ФМТ', 'ФМД', 'ФРТ', 'ФЕМП', 'ФПМ'])
            is_group = is_group or re.search(r'\d+-\d+|\d+-[А-ЯЁ]', potential_teacher)
            has_brackets = '[' in potential_teacher or ']' in potential_teacher
            is_room = 'ауд' in potential_teacher.lower()
            is_announcement = announcement and potential_teacher in announcement

            if not (is_group or has_brackets or is_room or is_announcement):
                # Проверяем что похоже на ФИО (минимум 3 слова)
                words = potential_teacher.split()
                if len(words) >= 3:
                    # Проверяем что первое слово - фамилия (заглавная, длиннее 2 символов, только буквы)
                    if words[0][0].isupper() and len(words[0]) > 2:
                        teacher_full = potential_teacher

        return subject, room, teacher_full, announcement

    def _extract_teacher_short(self, text: str) -> Optional[str]:
        """Извлекает сокращенное имя преподавателя"""
        lines = text.split('\n')
        for line in lines:
            # Ищем строку с инициалами (формат: Фамилия И.И.)
            if re.search(r'[А-ЯЁ][а-яё]+\s+[А-ЯЁ]\.[А-ЯЁ]\.', line):
                return line.strip()
        return None

    def _clean_subject(self, text: str) -> str:
        """Очищает название предмета"""
        lines = text.split('\n')
        if lines:
            subject = lines[0]
            # Удаляем тип в квадратных скобках
            subject = re.sub(r'\[.*?\]', '', subject).strip()
            subject = subject.strip('"').strip('"В"').strip()
            return subject
        return "Без назви"

    def _detect_lesson_type(self, text: str) -> LessonType:
        """Определяет тип занятия из текста"""
        return LessonType.from_ukrainian(text)

