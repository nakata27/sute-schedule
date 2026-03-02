"""Schedule service for managing course schedules with automatic tracking."""

import logging
from typing import Optional, Callable
from datetime import datetime, timedelta

from backend.fetcher import ScheduleFetcher
from backend.parser import ScheduleParser
from backend.storage import JsonStorage, SqliteStorage
from backend.models.schedule import ScheduleResponse, GroupInfo
from backend.config.settings import DATA_DIR

logger = logging.getLogger(__name__)


class ScheduleService:
    """Main service for managing schedules and course tracking."""

    def __init__(
        self,
        use_cache: bool = True,
        cache_lifetime_hours: int = 24,
        use_sqlite: bool = False,
        course_change_callback: Optional[Callable[[str, str, str], None]] = None
    ):
        """
        Initialize the schedule service.

        Args:
            use_cache: Enable caching of schedules.
            cache_lifetime_hours: Cache lifetime in hours.
            use_sqlite: Use SQLite storage instead of JSON.
            course_change_callback: Callback function triggered on course change.
        """
        self.use_cache = use_cache
        self.cache_lifetime = timedelta(hours=cache_lifetime_hours)
        self.course_change_callback = course_change_callback
        self._student_courses: dict[str, str] = {}

        self.fetcher = ScheduleFetcher()
        self.parser = ScheduleParser()

        schedules_dir = str(DATA_DIR / "schedules")
        if use_sqlite:
            self.storage = SqliteStorage(str(DATA_DIR / "schedules.db"))
        else:
            self.storage = JsonStorage(schedules_dir)

    def get_schedule(
        self,
        group_id: str,
        faculty_id: str,
        course: str,
        group_name: str,
        faculty_name: str,
        force_refresh: bool = False
    ) -> Optional[ScheduleResponse]:
        """
        Retrieve schedule for a group with automatic course tracking.

        Args:
            group_id: Group identifier.
            faculty_id: Faculty identifier.
            course: Course number.
            group_name: Group name.
            faculty_name: Faculty name.
            force_refresh: Force cache refresh.

        Returns:
            Schedule response or None on error.
        """
        self.track_student_course(group_id, course)

        if self.use_cache and not force_refresh:
            cached = self._get_from_cache(group_id)
            if cached:
                logger.info(f"Using cached schedule for group {group_id}")
                return cached

        logger.info(f"Fetching fresh schedule for group {group_id}")

        try:
            group_info = GroupInfo(
                group_id=group_id,
                group_name=group_name,
                faculty_id=faculty_id,
                faculty_name=faculty_name,
                course=course,
                last_updated=datetime.now()
            )

            html = self.fetcher.fetch_schedule(group_id, faculty_id, course)
            if not html:
                logger.error("Failed to fetch HTML")
                return None

            schedule = self.parser.parse(html, group_info)

            if self.use_cache:
                self.storage.save(schedule)
                logger.info(f"Schedule cached for group {group_id}")

            return schedule

        except Exception as e:
            logger.error(f"Error getting schedule: {e}", exc_info=True)

            if self.use_cache:
                logger.info("Attempting to use stale cache")
                return self._get_from_cache(group_id, ignore_lifetime=True)

            return None

    def _get_from_cache(
        self,
        group_id: str,
        ignore_lifetime: bool = False
    ) -> Optional[ScheduleResponse]:
        """
        Load schedule from cache.

        Args:
            group_id: Group identifier.
            ignore_lifetime: Ignore cache lifetime validation.

        Returns:
            Cached schedule or None.
        """
        try:
            schedule = self.storage.load(group_id)

            if not schedule:
                return None

            if not ignore_lifetime:
                age = datetime.now() - schedule.fetched_at
                if age > self.cache_lifetime:
                    logger.info(f"Cache expired for group {group_id} (age: {age})")
                    return None

            return schedule

        except Exception as e:
            logger.error(f"Error loading from cache: {e}")
            return None

    def track_student_course(self, group_id: str, new_course: str) -> bool:
        """
        Track course changes and invalidate cache if needed.

        Args:
            group_id: Group identifier.
            new_course: New course number.

        Returns:
            True if course changed, False otherwise.
        """
        timestamp = datetime.now().isoformat()
        old_course = self._student_courses.get(group_id)

        if old_course is None:
            self._student_courses[group_id] = new_course
            logger.info(
                f"[{timestamp}] Registered student course for group {group_id}: {new_course}"
            )
            return False

        if old_course != new_course:
            logger.warning(
                f"[{timestamp}] Course changed for group {group_id}: {old_course} -> {new_course}"
            )

            self.clear_cache(group_id)
            self._student_courses[group_id] = new_course

            if self.course_change_callback:
                try:
                    self.course_change_callback(group_id, old_course, new_course)
                    logger.info(
                        f"[{timestamp}] Course change callback executed for group {group_id}"
                    )
                except Exception as e:
                    logger.error(
                        f"[{timestamp}] Error executing course change callback: {e}",
                        exc_info=True
                    )

            return True

        return False

    def get_student_course(self, group_id: str) -> Optional[str]:
        """
        Get current tracked course for a group.

        Args:
            group_id: Group identifier.

        Returns:
            Current course number or None if not tracked.
        """
        course = self._student_courses.get(group_id)

        if course is None:
            logger.debug(f"No tracked course found for group {group_id}")
        else:
            logger.debug(f"Retrieved tracked course for group {group_id}: {course}")

        return course

    def clear_cache(self, group_id: Optional[str] = None):
        """
        Clear cache for a group or all groups.

        Args:
            group_id: Group identifier or None to clear all.
        """
        if group_id:
            self.storage.delete(group_id)
            logger.info(f"Cache cleared for group {group_id}")
        else:
            for gid in self.storage.list_cached_groups():
                self.storage.delete(gid)
            logger.info("All cache cleared")

    def get_cached_groups(self) -> list[str]:
        """
        Get list of groups with cached schedules.

        Returns:
            List of group identifiers.
        """
        return self.storage.list_cached_groups()

    def close(self):
        """Close connections."""
        self.fetcher.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
