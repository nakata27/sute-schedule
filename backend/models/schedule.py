"""Data models for schedule entries, groups, and API responses."""

from enum import Enum
from typing import Optional, List
from datetime import datetime, date
from pydantic import BaseModel, Field


class LessonType(str, Enum):
    """Типы занятий"""
    LECTURE = "lecture"  # Лекция
    PRACTICE = "practice"  # Практика
    SESSION = "session"  # Сессия
    EXAM = "exam"  # Экзамен
    CONSULTATION = "consultation"  # Консультация
    UNKNOWN = "unknown"  # Неизвестный тип

    @classmethod
    def from_ukrainian(cls, text: str) -> 'LessonType':
        """Определяет тип занятия по украинскому обозначению"""
        text_lower = text.lower()

        if any(x in text_lower for x in ['лк', 'лекція', 'лекция']):
            return cls.LECTURE
        elif any(x in text_lower for x in ['пз', 'практ', 'лаб']):
            return cls.PRACTICE
        elif any(x in text_lower for x in ['сесія', 'сессия', 'іспит', 'экзамен']):
            return cls.SESSION
        elif any(x in text_lower for x in ['екз', 'іспит']):
            return cls.EXAM
        elif any(x in text_lower for x in ['консульт']):
            return cls.CONSULTATION
        else:
            return cls.UNKNOWN


class Lesson(BaseModel):
    """Модель занятия (пары)"""

    # Основная информация
    lesson_number: int = Field(..., description="Номер пары (1-7)")
    start_time: str = Field(..., description="Время начала (HH:MM)")
    end_time: str = Field(..., description="Время окончания (HH:MM)")
    lesson_date: date = Field(..., description="Дата занятия")

    # Информация о предмете
    subject: str = Field(..., description="Название предмета")
    lesson_type: LessonType = Field(..., description="Тип занятия")

    # Место и преподаватель
    room: Optional[str] = Field(None, description="Аудитория")
    teacher: Optional[str] = Field(None, description="Преподаватель (сокращенно)")
    teacher_full: Optional[str] = Field(None, description="Полное имя преподавателя")

    # Дополнительная информация
    notes: Optional[str] = Field(None, description="Комментарий")
    announcement: Optional[str] = Field(None, description="Объявление преподавателя")
    added_date: Optional[datetime] = Field(None, description="Дата добавления в расписание")

    # Метаданные
    raw_html: Optional[str] = Field(None, description="Исходный HTML (для отладки)")

    model_config = {"use_enum_values": True}


class DaySchedule(BaseModel):
    """Расписание на один день"""

    day_date: date = Field(..., description="Дата")
    day_of_week: int = Field(..., description="День недели (0=понедельник, 6=воскресенье)")
    lessons: List[Lesson] = Field(default_factory=list, description="Список занятий")

    @property
    def has_lessons(self) -> bool:
        """Проверяет, есть ли занятия в этот день"""
        return len(self.lessons) > 0

    @property
    def day_name_uk(self) -> str:
        """Название дня недели на украинском"""
        days = ["Понеділок", "Вівторок", "Середа", "Четвер", "П'ятниця", "Субота", "Неділя"]
        return days[self.day_of_week]

    @property
    def day_name_en(self) -> str:
        """Название дня недели на английском"""
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        return days[self.day_of_week]


class WeekSchedule(BaseModel):
    """Расписание на неделю"""

    week_number: int = Field(..., description="Номер недели")
    week_start: date = Field(..., description="Начало недели (понедельник)")
    week_end: date = Field(..., description="Конец недели (воскресенье)")
    days: List[DaySchedule] = Field(default_factory=list, description="Расписание по дням")

    @property
    def date_range_str(self) -> str:
        """Диапазон дат недели в формате DD.MM.YYYY - DD.MM.YYYY"""
        return f"{self.week_start.strftime('%d.%m.%Y')} - {self.week_end.strftime('%d.%m.%Y')}"

    def get_day(self, date: date) -> Optional[DaySchedule]:
        """Получить расписание на конкретный день"""
        for day in self.days:
            if day.day_date == date:
                return day
        return None


class GroupInfo(BaseModel):
    """Информация о группе"""

    group_id: str = Field(..., description="ID группы")
    group_name: str = Field(..., description="Название группы")
    faculty_id: str = Field(..., description="ID факультета")
    faculty_name: str = Field(..., description="Название факультета")
    course: str = Field(..., description="Курс")

    # Кэшированные данные
    last_updated: Optional[datetime] = Field(None, description="Время последнего обновления")

    model_config = {"use_enum_values": True}


class ScheduleResponse(BaseModel):
    """Ответ с расписанием"""

    group_info: GroupInfo = Field(..., description="Информация о группе")
    weeks: List[WeekSchedule] = Field(default_factory=list, description="Расписание по неделям")
    fetched_at: datetime = Field(default_factory=datetime.now, description="Время получения данных")

    def get_week(self, week_number: int) -> Optional[WeekSchedule]:
        """Получить расписание на конкретную неделю"""
        for week in self.weeks:
            if week.week_number == week_number:
                return week
        return None

    def get_current_week(self) -> Optional[WeekSchedule]:
        """Получить расписание на текущую неделю"""
        today = date.today()
        for week in self.weeks:
            if week.week_start <= today <= week.week_end:
                return week
        return None

