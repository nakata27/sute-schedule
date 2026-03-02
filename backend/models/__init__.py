"""
Модели данных для приложения расписания MIA
"""

from .schedule import (
    LessonType,
    Lesson,
    DaySchedule,
    WeekSchedule,
    GroupInfo
)

__all__ = [
    'LessonType',
    'Lesson',
    'DaySchedule',
    'WeekSchedule',
    'GroupInfo'
]
