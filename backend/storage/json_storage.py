"""
JSON Storage - сохранение расписания в JSON файлы
"""

import json
from pathlib import Path
from typing import Optional
from datetime import datetime
import logging

from backend.models.schedule import ScheduleResponse, GroupInfo

logger = logging.getLogger(__name__)


class JsonStorage:
    """
    Хранилище расписания в JSON формате
    """

    def __init__(self, base_dir: str = "data/schedules"):
        """
        Args:
            base_dir: Базовая директория для хранения данных
        """
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def save(self, schedule: ScheduleResponse) -> str:
        """
        Сохраняет расписание в JSON файл

        Args:
            schedule: Расписание для сохранения

        Returns:
            Путь к сохраненному файлу
        """
        group_id = schedule.group_info.group_id

        # Создаем имя файла с timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"schedule_{group_id}_{timestamp}.json"
        filepath = self.base_dir / filename

        # Также создаем "текущий" файл без timestamp
        current_filename = f"schedule_{group_id}_current.json"
        current_filepath = self.base_dir / current_filename

        # Сериализуем в JSON
        data = schedule.model_dump(mode='json')

        # Сохраняем оба файла
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)

        with open(current_filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)

        logger.info(f"Schedule saved to {filepath}")
        return str(filepath)

    def load(self, group_id: str, use_current: bool = True) -> Optional[ScheduleResponse]:
        """
        Загружает расписание из JSON файла

        Args:
            group_id: ID группы
            use_current: Использовать "текущий" файл

        Returns:
            Расписание или None, если файл не найден
        """
        if use_current:
            filename = f"schedule_{group_id}_current.json"
        else:
            # Ищем последний файл для группы
            pattern = f"schedule_{group_id}_*.json"
            files = sorted(self.base_dir.glob(pattern), reverse=True)

            if not files:
                logger.warning(f"No schedule files found for group {group_id}")
                return None

            filename = files[0].name

        filepath = self.base_dir / filename

        if not filepath.exists():
            logger.warning(f"Schedule file not found: {filepath}")
            return None

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Десериализуем из JSON
            schedule = ScheduleResponse.model_validate(data)
            logger.info(f"Schedule loaded from {filepath}")
            return schedule

        except Exception as e:
            logger.error(f"Error loading schedule from {filepath}: {e}")
            return None

    def load_group_info(self, group_id: str) -> Optional[GroupInfo]:
        """
        Загружает только информацию о группе

        Args:
            group_id: ID группы

        Returns:
            Информация о группе или None
        """
        schedule = self.load(group_id)
        return schedule.group_info if schedule else None

    def delete(self, group_id: str):
        """
        Удаляет все файлы расписания для группы

        Args:
            group_id: ID группы
        """
        pattern = f"schedule_{group_id}_*.json"
        files = list(self.base_dir.glob(pattern))

        for filepath in files:
            filepath.unlink()
            logger.info(f"Deleted {filepath}")

    def list_cached_groups(self) -> list[str]:
        """
        Возвращает список ID групп с кэшированным расписанием

        Returns:
            Список ID групп
        """
        pattern = "schedule_*_current.json"
        files = self.base_dir.glob(pattern)

        group_ids = []
        for filepath in files:
            # Извлекаем group_id из имени файла
            parts = filepath.stem.split('_')
            if len(parts) >= 2:
                group_id = parts[1]
                group_ids.append(group_id)

        return group_ids

