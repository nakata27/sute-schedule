"""
SQLite Storage - сохранение расписания в SQLite БД (опциональное)
"""

import sqlite3
from pathlib import Path
from typing import Optional, List
from datetime import datetime, date
import json
import logging

from ..models.schedule import (
    ScheduleResponse,
    WeekSchedule,
    DaySchedule,
    Lesson,
    GroupInfo,
    LessonType
)

logger = logging.getLogger(__name__)


class SqliteStorage:
    """
    Хранилище расписания в SQLite базе данных
    """

    def __init__(self, db_path: str = "data/schedules.db"):
        """
        Args:
            db_path: Путь к файлу базы данных
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        """Инициализирует структуру базы данных"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Таблица групп
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS groups (
                    group_id TEXT PRIMARY KEY,
                    group_name TEXT NOT NULL,
                    faculty_id TEXT NOT NULL,
                    faculty_name TEXT NOT NULL,
                    course TEXT NOT NULL,
                    last_updated TIMESTAMP
                )
            ''')

            # Таблица недель
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS weeks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    group_id TEXT NOT NULL,
                    week_number INTEGER NOT NULL,
                    week_start DATE NOT NULL,
                    week_end DATE NOT NULL,
                    FOREIGN KEY (group_id) REFERENCES groups(group_id),
                    UNIQUE(group_id, week_number)
                )
            ''')

            # Таблица занятий
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS lessons (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    week_id INTEGER NOT NULL,
                    lesson_date DATE NOT NULL,
                    day_of_week INTEGER NOT NULL,
                    lesson_number INTEGER NOT NULL,
                    start_time TEXT NOT NULL,
                    end_time TEXT NOT NULL,
                    subject TEXT NOT NULL,
                    lesson_type TEXT NOT NULL,
                    room TEXT,
                    teacher TEXT,
                    teacher_full TEXT,
                    comment TEXT,
                    added_date TIMESTAMP,
                    raw_html TEXT,
                    FOREIGN KEY (week_id) REFERENCES weeks(id)
                )
            ''')

            # Индексы
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_lessons_week_date 
                ON lessons(week_id, lesson_date)
            ''')

            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_weeks_group 
                ON weeks(group_id)
            ''')

            conn.commit()
            logger.info("Database initialized")

    def save(self, schedule: ScheduleResponse):
        """
        Сохраняет расписание в базу данных

        Args:
            schedule: Расписание для сохранения
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            group_info = schedule.group_info

            # Сохраняем информацию о группе
            cursor.execute('''
                INSERT OR REPLACE INTO groups 
                (group_id, group_name, faculty_id, faculty_name, course, last_updated)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                group_info.group_id,
                group_info.group_name,
                group_info.faculty_id,
                group_info.faculty_name,
                group_info.course,
                datetime.now()
            ))

            # Удаляем старые данные для этой группы
            cursor.execute('DELETE FROM weeks WHERE group_id = ?', (group_info.group_id,))

            # Сохраняем недели и занятия
            for week in schedule.weeks:
                cursor.execute('''
                    INSERT INTO weeks (group_id, week_number, week_start, week_end)
                    VALUES (?, ?, ?, ?)
                ''', (
                    group_info.group_id,
                    week.week_number,
                    week.week_start,
                    week.week_end
                ))

                week_id = cursor.lastrowid

                # Сохраняем занятия
                for day in week.days:
                    for lesson in day.lessons:
                        cursor.execute('''
                            INSERT INTO lessons 
                            (week_id, lesson_date, day_of_week, lesson_number, 
                             start_time, end_time, subject, lesson_type, 
                             room, teacher, teacher_full, notes, added_date, raw_html)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            week_id,
                            lesson.lesson_date,
                            day.day_of_week,
                            lesson.lesson_number,
                            lesson.start_time,
                            lesson.end_time,
                            lesson.subject,
                            lesson.lesson_type.value,
                            lesson.room,
                            lesson.teacher,
                            lesson.teacher_full,
                            lesson.notes,
                            lesson.added_date,
                            lesson.raw_html
                        ))

            conn.commit()
            logger.info(f"Schedule for group {group_info.group_id} saved to database")

    def load(self, group_id: str) -> Optional[ScheduleResponse]:
        """
        Загружает расписание из базы данных

        Args:
            group_id: ID группы

        Returns:
            Расписание или None
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # Загружаем информацию о группе
            cursor.execute('SELECT * FROM groups WHERE group_id = ?', (group_id,))
            group_row = cursor.fetchone()

            if not group_row:
                logger.warning(f"Group {group_id} not found in database")
                return None

            group_info = GroupInfo(
                group_id=group_row['group_id'],
                group_name=group_row['group_name'],
                faculty_id=group_row['faculty_id'],
                faculty_name=group_row['faculty_name'],
                course=group_row['course'],
                last_updated=datetime.fromisoformat(group_row['last_updated']) if group_row['last_updated'] else None
            )

            # Загружаем недели
            cursor.execute('''
                SELECT * FROM weeks 
                WHERE group_id = ? 
                ORDER BY week_number
            ''', (group_id,))

            week_rows = cursor.fetchall()
            weeks = []

            for week_row in week_rows:
                week_id = week_row['id']

                # Загружаем занятия для недели
                cursor.execute('''
                    SELECT * FROM lessons 
                    WHERE week_id = ? 
                    ORDER BY lesson_date, lesson_number
                ''', (week_id,))

                lesson_rows = cursor.fetchall()

                # Группируем занятия по дням
                days_dict = {}
                for lesson_row in lesson_rows:
                    lesson_date = date.fromisoformat(lesson_row['lesson_date'])

                    if lesson_date not in days_dict:
                        days_dict[lesson_date] = DaySchedule(
                            day_date=lesson_date,
                            day_of_week=lesson_row['day_of_week'],
                            lessons=[]
                        )

                    lesson = Lesson(
                        lesson_number=lesson_row['lesson_number'],
                        start_time=lesson_row['start_time'],
                        end_time=lesson_row['end_time'],
                        lesson_date=lesson_date,
                        subject=lesson_row['subject'],
                        lesson_type=LessonType(lesson_row['lesson_type']),
                        room=lesson_row['room'],
                        teacher=lesson_row['teacher'],
                        teacher_full=lesson_row['teacher_full'],
                        notes=lesson_row['notes'],
                        added_date=datetime.fromisoformat(lesson_row['added_date']) if lesson_row['added_date'] else None,
                        raw_html=lesson_row['raw_html']
                    )

                    days_dict[lesson_date].lessons.append(lesson)

                # Создаем WeekSchedule
                days = [days_dict[d] for d in sorted(days_dict.keys())]

                week = WeekSchedule(
                    week_number=week_row['week_number'],
                    week_start=date.fromisoformat(week_row['week_start']),
                    week_end=date.fromisoformat(week_row['week_end']),
                    days=days
                )

                weeks.append(week)

            schedule = ScheduleResponse(
                group_info=group_info,
                weeks=weeks,
                fetched_at=group_info.last_updated or datetime.now()
            )

            logger.info(f"Schedule for group {group_id} loaded from database")
            return schedule

    def delete(self, group_id: str):
        """
        Удаляет расписание группы из базы данных

        Args:
            group_id: ID группы
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM groups WHERE group_id = ?', (group_id,))
            conn.commit()
            logger.info(f"Schedule for group {group_id} deleted from database")

    def list_cached_groups(self) -> List[str]:
        """
        Возвращает список ID групп с кэшированным расписанием

        Returns:
            Список ID групп
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT group_id FROM groups')
            rows = cursor.fetchall()
            return [row[0] for row in rows]

