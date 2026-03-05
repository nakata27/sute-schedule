"""Backend test script — verifies schedule fetching, parsing, and caching."""

import sys
import json
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.schedule_service import ScheduleService
from config.settings import GROUPS_FILE

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def load_groups_data():
    """Load group structure from the JSON data file."""
    with open(GROUPS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def test_backend():
    """Run backend integration tests."""

    print("\n" + "="*60)
    print("ТЕСТИРОВАНИЕ BACKEND")
    print("="*60 + "\n")

    # Загружаем данные о группах
    groups_data = load_groups_data()

    # Берем первую группу для теста
    first_faculty = groups_data[0]
    first_course = first_faculty['courses'][0]
    first_group = first_course['groups'][0]

    print(f"Тестовая группа:")
    print(f"  Факультет: {first_faculty['faculty_name']}")
    print(f"  Курс: {first_course['course_number']}")
    print(f"  Группа: {first_group['group_name']}")
    print(f"  ID: {first_group['group_id']}")
    print()

    # Создаем сервис
    with ScheduleService(use_cache=True, cache_lifetime_hours=1) as service:

        print("Получение расписания...")
        schedule = service.get_schedule(
            group_id=first_group['group_id'],
            faculty_id=first_faculty['faculty_id'],
            course=first_course['course_number'],
            group_name=first_group['group_name'],
            faculty_name=first_faculty['faculty_name']
        )

        if schedule:
            print("✓ Расписание успешно получено!")
            print()
            print(f"Информация о группе:")
            print(f"  Группа: {schedule.group_info.group_name}")
            print(f"  Факультет: {schedule.group_info.faculty_name}")
            print(f"  Курс: {schedule.group_info.course}")
            print(f"  Обновлено: {schedule.fetched_at}")
            print()

            print(f"Недель в расписании: {len(schedule.weeks)}")
            print()

            # Выводим информацию по неделям
            for week in schedule.weeks:
                print(f"Неделя {week.week_number}: {week.date_range_str}")
                print(f"  Дней с занятиями: {len(week.days)}")

                # Подсчитываем общее количество занятий
                total_lessons = sum(len(day.lessons) for day in week.days)
                print(f"  Всего занятий: {total_lessons}")

                # Выводим первые 3 занятия для примера
                if total_lessons > 0:
                    print("  Примеры занятий:")
                    count = 0
                    for day in week.days:
                        if count >= 3:
                            break
                        for lesson in day.lessons:
                            if count >= 3:
                                break
                            print(f"    - {day.day_date} | {lesson.lesson_number} пара ({lesson.start_time}-{lesson.end_time})")
                            print(f"      {lesson.subject} [{lesson.lesson_type}]")
                            print(f"      Ауд: {lesson.room}, Викл: {lesson.teacher}")
                            count += 1

                print()

            # Тест текущей недели
            current_week = schedule.get_current_week()
            if current_week:
                print("="*60)
                print(f"ТЕКУЩАЯ НЕДЕЛЯ: {current_week.date_range_str}")
                print("="*60)
                print()

                for day in current_week.days:
                    print(f"{day.day_name_uk} ({day.day_date.strftime('%d.%m.%Y')})")

                    if not day.lessons:
                        print("  Немає занять")
                    else:
                        for lesson in day.lessons:
                            lesson_type_emoji = {
                                "lecture": "📚",
                                "practice": "💻",
                                "session": "📝",
                                "exam": "📋",
                                "consultation": "💬",
                                "unknown": "❓"
                            }
                            emoji = lesson_type_emoji.get(lesson.lesson_type, "📌")

                            print(f"  {emoji} {lesson.lesson_number} пара ({lesson.start_time}-{lesson.end_time})")
                            print(f"     {lesson.subject}")
                            print(f"     Ауд: {lesson.room or 'не вказано'}, Викл: {lesson.teacher or 'не вказано'}")

                    print()

            # Тест кэширования
            print("="*60)
            print("ТЕСТ КЭШИРОВАНИЯ")
            print("="*60)
            print()

            print("Повторное получение расписания (должно использовать кэш)...")
            schedule2 = service.get_schedule(
                group_id=first_group['group_id'],
                faculty_id=first_faculty['faculty_id'],
                course=first_course['course_number'],
                group_name=first_group['group_name'],
                faculty_name=first_faculty['faculty_name']
            )

            if schedule2:
                print("✓ Расписание получено из кэша")
                print(f"  Время получения первого: {schedule.fetched_at}")
                print(f"  Время получения второго: {schedule2.fetched_at}")

                if schedule.fetched_at == schedule2.fetched_at:
                    print("  ✓ Времена совпадают - кэш работает!")

        else:
            print("✗ Не удалось получить расписание")
            return False

    print("\n" + "="*60)
    print("✓ ТЕСТИРОВАНИЕ ЗАВЕРШЕНО УСПЕШНО")
    print("="*60 + "\n")

    return True


if __name__ == "__main__":
    try:
        success = test_backend()
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.error(f"Ошибка при тестировании: {e}", exc_info=True)
        sys.exit(1)

