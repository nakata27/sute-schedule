"""
Storage модуль - сохранение и загрузка данных
"""

from .json_storage import JsonStorage
from .sqlite_storage import SqliteStorage

__all__ = ['JsonStorage', 'SqliteStorage']

