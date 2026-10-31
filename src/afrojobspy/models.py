"""Standardized data models and geographic configuration for African job listings."""

from __future__ import annotations

from typing import Dict, List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator


class JobPost(BaseModel):
    """
    Normalized job posting schema used across all African job-board adapters.

    Designed for interoperability with pandas DataFrames, downstream ATS tools,
    and labour-market analytics pipelines.
    """

    id: str = Field(default_factory=lambda: str(uuid4()))
    title: str
    company: Optional[str] = "N/A"
    city: Optional[str] = None
    country: Optional[str] = None
    location: Optional[str] = None
    is_remote: Optional[bool] = False
    employment_type: Optional[str] = None  # full_time | part_time | contract | internship | temporary
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    currency: Optional[str] = None
    experience_level: Optional[str] = None  # entry | mid | senior | executive
    skills: List[str] = Field(default_factory=list)
    site_name: str
    job_url: str
    description: Optional[str] = None
    date_posted: Optional[str] = None
    deadline: Optional[str] = None

    @field_validator("title", "job_url", "site_name")
    @classmethod
    def non_empty(cls, v: str) -> str:
        if not v or not str(v).strip():
            raise ValueError("Field cannot be empty")
        return str(v).strip()

    def to_dict(self) -> dict:
        """Pydantic v1/v2 compatible dictionary export."""
        if hasattr(self, "model_dump"):
            return self.model_dump()
        return self.dict()  # type: ignore[attr-defined]


# Canonical region → country → site keys mapping
REGION_MAP: Dict[str, Dict[str, List[str]]] = {
    "east_africa": {
        "ethiopia": [
            "ethiojobs",
            "afriwork",
            "hahujobs",
            "geezjobs",
            "dereja",
            "addisjobs",
            "jobsethio",
            "telegram_jobs",
        ],
        "kenya": ["brightermonday", "fuzu", "myjobmag"],
        "uganda": ["brightermonday", "fuzu"],
    },
    "west_africa": {
        "nigeria": ["jobberman", "myjobmag"],
        "ghana": ["jobberman", "myjobmag"],
    },
    "southern_africa": {
        "south_africa": ["careerjunction", "careers24"],
    },
    "north_africa": {
        "egypt": ["wuzzuf"],
    },
    "pan_african": {
        "continental": ["au_jobs", "reliefweb", "unjobs"],
    },
}

# Flat lookup: country → list of site keys
COUNTRY_SITES: Dict[str, List[str]] = {}
for _region, countries in REGION_MAP.items():
    for country, sites in countries.items():
        COUNTRY_SITES.setdefault(country, [])
        for s in sites:
            if s not in COUNTRY_SITES[country]:
                COUNTRY_SITES[country].append(s)

# All known site keys (union)
ALL_SITE_KEYS: List[str] = sorted(
    {s for sites in COUNTRY_SITES.values() for s in sites}
)
