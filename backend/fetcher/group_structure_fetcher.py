"""Direct MIA scraper for faculties/courses/groups structure."""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass
from typing import Any, Iterable, Optional

from bs4 import BeautifulSoup

from .schedule_fetcher import ScheduleFetcher, ScheduleFetcherError

logger = logging.getLogger(__name__)


@dataclass
class RequestStatus:
    method: str
    url: str
    status_code: int
    ok: bool
    error: Optional[str] = None


class GroupStructureFetcher:
    """Scrapes MIA to produce current faculties -> courses -> groups tree."""

    COURSE_RANGE = [str(i) for i in range(1, 7)]

    def __init__(self, fetcher: Optional[ScheduleFetcher] = None):
        self.fetcher = fetcher or ScheduleFetcher(timeout=20)
        self.request_statuses: list[RequestStatus] = []
        self._csrf_token: Optional[str] = None

    def _track_status(
        self,
        method: str,
        url: str,
        status_code: int,
        ok: bool,
        error: Optional[str] = None
    ):
        self.request_statuses.append(
            RequestStatus(
                method=method.upper(),
                url=url,
                status_code=status_code,
                ok=ok,
                error=error,
            )
        )

    def _request(self, method: str, url: str, **kwargs):
        try:
            response = self.fetcher._request(method, url, **kwargs)  # noqa: SLF001
            self._track_status(method, url, response.status_code, response.ok)
            return response
        except Exception as e:
            self._track_status(method, url, 0, False, str(e))
            raise

    def _get_base_page(self) -> str:
        response = self._request("GET", self.fetcher.SCHEDULE_URL)
        response.raise_for_status()
        return response.text

    def _extract_csrf(self, html: str) -> Optional[str]:
        soup = BeautifulSoup(html, "html.parser")
        csrf_input = soup.find("input", {"name": "_csrf-frontend"})
        return csrf_input.get("value") if csrf_input else None

    def _extract_faculties(self, html: str) -> list[dict[str, str]]:
        soup = BeautifulSoup(html, "html.parser")
        select = soup.find("select", {"name": "TimeTableForm[facultyId]"})
        faculties: list[dict[str, str]] = []
        if not select:
            return faculties
        for opt in select.find_all("option"):
            value = (opt.get("value") or "").strip()
            name = opt.get_text(strip=True)
            if not value or not name:
                continue
            faculties.append({"faculty_id": value, "faculty_name": name})
        return faculties

    def _extract_endpoints(self, html: str) -> dict[str, list[str]]:
        matches = set(re.findall(r"/time-table/[^\"'\\)\s]+", html))
        courses = []
        groups = []
        for endpoint in sorted(matches):
            low = endpoint.lower()
            if any(token in low for token in ("course", "kurs")):
                courses.append(endpoint)
            if "group" in low and "time-table/group" not in low:
                groups.append(endpoint)

        if not courses:
            courses = [
                "/time-table/group/get-courses",
                "/time-table/group/course-list",
                "/time-table/group/courses",
            ]
        if not groups:
            groups = [
                "/time-table/group/get-groups",
                "/time-table/group/group-list",
                "/time-table/group/groups",
            ]
        return {"courses": courses, "groups": groups}

    def _parse_depdrop_json(self, payload: Any) -> list[dict[str, str]]:
        if not isinstance(payload, dict):
            return []
        output = payload.get("output")
        if not isinstance(output, list):
            return []
        items = []
        for item in output:
            if not isinstance(item, dict):
                continue
            item_id = str(item.get("id", "")).strip()
            item_name = str(item.get("name", "")).strip()
            if item_id and item_name:
                items.append({"id": item_id, "name": item_name})
        return items

    def _post_depdrop(self, endpoint: str, depdrop_parents: Iterable[str]) -> list[dict[str, str]]:
        url = f"{self.fetcher.BASE_URL}{endpoint}"
        token = self._csrf_token or ""
        payloads = [
            {"depdrop_parents[]": list(depdrop_parents)},
            {"depdrop_parents": list(depdrop_parents)},
            {"parents[]": list(depdrop_parents)},
            {"parents": list(depdrop_parents)},
        ]
        headers = {
            "X-Requested-With": "XMLHttpRequest",
            "Referer": self.fetcher.SCHEDULE_URL,
        }
        if token:
            headers["X-CSRF-Token"] = token

        for payload in payloads:
            try:
                response = self._request("POST", url, data=payload, headers=headers)
                if response.status_code >= 400:
                    continue
                try:
                    parsed = response.json()
                except ValueError:
                    continue
                items = self._parse_depdrop_json(parsed)
                if items:
                    return items
            except Exception:
                continue
        return []

    def _fetch_groups_by_schedule_probe(self, faculty_id: str, course_number: str) -> list[dict[str, str]]:
        """Fallback probe: parse select options from timetable response for a course."""
        if not self._csrf_token:
            return []

        form_data = {
            "_csrf-frontend": self._csrf_token,
            "TimeTableForm[facultyId]": faculty_id,
            "TimeTableForm[course]": course_number,
        }
        try:
            response = self._request(
                "POST",
                f"{self.fetcher.SCHEDULE_URL}?type=0",
                data=form_data,
                headers={"Referer": self.fetcher.SCHEDULE_URL},
            )
            if response.status_code >= 400:
                return []
            soup = BeautifulSoup(response.text, "html.parser")
            select = soup.find("select", {"name": "TimeTableForm[groupId]"})
            if not select:
                return []
            groups = []
            for opt in select.find_all("option"):
                value = (opt.get("value") or "").strip()
                name = opt.get_text(strip=True)
                if value and name:
                    groups.append({"group_id": value, "group_name": name})
            return groups
        except Exception:
            return []

    def fetch_structure(self) -> list[dict[str, Any]]:
        html = self._get_base_page()
        self._csrf_token = self._extract_csrf(html)
        faculties = self._extract_faculties(html)
        endpoints = self._extract_endpoints(html)

        structure: list[dict[str, Any]] = []
        for faculty in faculties:
            faculty_id = faculty["faculty_id"]
            courses_data: list[dict[str, Any]] = []

            courses = []
            for endpoint in endpoints["courses"]:
                courses = self._post_depdrop(endpoint, [faculty_id])
                if courses:
                    break
            if not courses:
                courses = [{"id": c, "name": c} for c in self.COURSE_RANGE]

            for course in courses:
                course_number = str(course["id"]).strip()
                groups = []
                for endpoint in endpoints["groups"]:
                    groups_depdrop = self._post_depdrop(endpoint, [faculty_id, course_number])
                    if groups_depdrop:
                        groups = [
                            {"group_id": item["id"], "group_name": item["name"]}
                            for item in groups_depdrop
                        ]
                        break

                if not groups:
                    groups = self._fetch_groups_by_schedule_probe(faculty_id, course_number)

                if groups:
                    courses_data.append(
                        {
                            "course_number": course_number,
                            "groups": groups,
                        }
                    )

            if courses_data:
                structure.append(
                    {
                        "faculty_name": faculty["faculty_name"],
                        "faculty_id": faculty_id,
                        "courses": courses_data,
                    }
                )

        if not structure:
            raise ScheduleFetcherError("Failed to scrape MIA structure: empty result")
        return structure

    def save_structure(self, file_path: str) -> list[dict[str, Any]]:
        structure = self.fetch_structure()
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(structure, f, ensure_ascii=False, indent=4)
        return structure

