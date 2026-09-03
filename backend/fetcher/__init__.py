"""Fetcher module — retrieves schedule data from the MIA site."""

from .schedule_fetcher import ScheduleFetcher
from .group_structure_fetcher import GroupStructureFetcher

__all__ = ['ScheduleFetcher', 'GroupStructureFetcher']
