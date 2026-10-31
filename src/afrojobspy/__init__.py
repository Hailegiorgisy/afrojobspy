"""
AfroJobsPy – concurrent job scraping for African employment platforms.

Public API:
    scrape_jobs(...)  → pandas.DataFrame
    list_sites()      → dict of available sites / regions / countries
"""

from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, List, Optional, Type

import pandas as pd

from afrojobspy.models import (
    ALL_SITE_KEYS,
    COUNTRY_SITES,
    REGION_MAP,
    JobPost,
)
from afrojobspy.scrapers.addisjobs import AddisJobsScraper
from afrojobspy.scrapers.afriwork import AfriworkScraper
from afrojobspy.scrapers.aujobs import AUJobsScraper
from afrojobspy.scrapers.base import BaseScraper
from afrojobspy.scrapers.brightermonday import BrighterMondayScraper
from afrojobspy.scrapers.careerjunction import CareerJunctionScraper
from afrojobspy.scrapers.careers24 import Careers24Scraper
from afrojobspy.scrapers.dereja import DerejaScraper
from afrojobspy.scrapers.ethiojobs import EthiojobsScraper
from afrojobspy.scrapers.fuzu import FuzuScraper
from afrojobspy.scrapers.geezjobs import GeezJobsScraper
from afrojobspy.scrapers.hahujobs import HahuJobsScraper
from afrojobspy.scrapers.jobberman import JobbermanScraper
from afrojobspy.scrapers.jobsethio import JobsEthioScraper
from afrojobspy.scrapers.myjobmag import MyJobMagScraper
from afrojobspy.scrapers.reliefweb import ReliefWebScraper
from afrojobspy.scrapers.telegram_jobs import TelegramJobsScraper
from afrojobspy.scrapers.unjobs import UNJobsScraper
from afrojobspy.scrapers.wuzzuf import WuzzufScraper

__version__ = "0.2.0"
__all__ = [
    "scrape_jobs",
    "list_sites",
    "JobPost",
    "SCRAPER_REGISTRY",
    "__version__",
]

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Full scraper registry – every implemented adapter is registered here
# ---------------------------------------------------------------------------
SCRAPER_REGISTRY: Dict[str, Type[BaseScraper]] = {
    "ethiojobs": EthiojobsScraper,
    "afriwork": AfriworkScraper,
    "hahujobs": HahuJobsScraper,
    "geezjobs": GeezJobsScraper,
    "dereja": DerejaScraper,
    "addisjobs": AddisJobsScraper,
    "jobsethio": JobsEthioScraper,
    "telegram_jobs": TelegramJobsScraper,
    "brightermonday": BrighterMondayScraper,
    "fuzu": FuzuScraper,
    "jobberman": JobbermanScraper,
    "myjobmag": MyJobMagScraper,
    "careerjunction": CareerJunctionScraper,
    "careers24": Careers24Scraper,
    "wuzzuf": WuzzufScraper,
    "au_jobs": AUJobsScraper,
    "reliefweb": ReliefWebScraper,
    "unjobs": UNJobsScraper,
}


def list_sites() -> Dict[str, Any]:
    """
    Return a structured catalogue of supported sites, countries and regions.

    Useful for CLI discovery and programmatic introspection.
    """
    return {
        "sites": sorted(SCRAPER_REGISTRY.keys()),
        "countries": {k: v for k, v in sorted(COUNTRY_SITES.items())},
        "regions": {k: list(v.keys()) for k, v in REGION_MAP.items()},
        "version": __version__,
    }


def _resolve_sites(
    sites: Optional[List[str]] = None,
    country: Optional[str] = None,
    region: Optional[str] = None,
) -> List[str]:
    """
    Resolve the final list of site keys from the three possible filters.

    Priority: explicit `sites` (including empty list) > `country` > `region` > all registered sites.
    Only keys present in SCRAPER_REGISTRY are retained.
    """
    if sites is not None:
        resolved = [s.lower().strip() for s in sites]
    elif country:
        key = country.lower().strip().replace(" ", "_")
        resolved = list(COUNTRY_SITES.get(key, []))
        if not resolved:
            logger.warning("No sites mapped for country '%s'", country)
    elif region:
        key = region.lower().strip().replace(" ", "_")
        countries = REGION_MAP.get(key, {})
        resolved = []
        for c_sites in countries.values():
            resolved.extend(c_sites)
        # de-duplicate while preserving order
        seen: set = set()
        uniq = []
        for s in resolved:
            if s not in seen:
                seen.add(s)
                uniq.append(s)
        resolved = uniq
        if not resolved:
            logger.warning("No sites mapped for region '%s'", region)
    else:
        resolved = list(SCRAPER_REGISTRY.keys())

    # Keep only registered adapters
    final = [s for s in resolved if s in SCRAPER_REGISTRY]
    unknown = set(resolved) - set(final)
    for u in unknown:
        logger.warning("Unknown or unregistered site key '%s' – skipping", u)
    return final


def _scrape_one(
    site_key: str,
    search_term: str,
    location: str,
    results_wanted: int,
    proxies: Optional[List[str]],
) -> List[JobPost]:
    """Worker function executed inside the thread pool."""
    scraper_cls = SCRAPER_REGISTRY[site_key]
    try:
        scraper = scraper_cls(proxies=proxies)
        jobs = scraper.scrape(
            search_term=search_term,
            location=location,
            results_wanted=results_wanted,
        )
        logger.info("Scraped %d jobs from %s", len(jobs), site_key)
        return jobs
    except Exception as exc:  # noqa: BLE001 – isolate per-site failures
        logger.error("Error scraping %s: %s", site_key, exc, exc_info=False)
        return []


def scrape_jobs(
    search_term: str = "",
    location: str = "",
    results_wanted: int = 15,
    sites: Optional[List[str]] = None,
    country: Optional[str] = None,
    region: Optional[str] = None,
    proxies: Optional[List[str]] = None,
    max_workers: int = 6,
) -> pd.DataFrame:
    """
    Concurrently scrape multiple African job boards and return a normalised
    pandas DataFrame.

    Parameters
    ----------
    search_term :
        Free-text keyword (e.g. "Data Scientist", "Public Health").
    location :
        Optional free-text location hint passed to individual scrapers.
    results_wanted :
        Approximate number of listings desired *per site*.
    sites :
        Explicit list of site keys (e.g. ``["ethiojobs", "brightermonday"]``).
        Takes precedence over ``country`` / ``region``.
    country :
        Country filter (e.g. ``"ethiopia"``, ``"kenya"``). Ignored if ``sites``
        is supplied.
    region :
        Regional cluster (e.g. ``"east_africa"``, ``"west_africa"``).
        Ignored if ``sites`` or ``country`` is supplied.
    proxies :
        Optional list of proxy URLs (``http://user:pass@host:port``).
        Rotated on transient failures.
    max_workers :
        Maximum number of concurrent scraper threads (default 6).

    Returns
    -------
    pandas.DataFrame
        Columns match the ``JobPost`` schema. Exact URL duplicates are removed.
    """
    target_sites = _resolve_sites(sites=sites, country=country, region=region)
    if not target_sites:
        logger.warning("No valid sites selected – returning empty DataFrame")
        return _empty_df()

    logger.info(
        "Scraping %d site(s) for '%s' (results_wanted=%d, workers=%d)",
        len(target_sites),
        search_term or "(any)",
        results_wanted,
        max_workers,
    )

    all_jobs: List[JobPost] = []
    with ThreadPoolExecutor(max_workers=min(max_workers, len(target_sites))) as pool:
        futures = {
            pool.submit(
                _scrape_one,
                site_key,
                search_term,
                location,
                results_wanted,
                proxies,
            ): site_key
            for site_key in target_sites
        }
        for fut in as_completed(futures):
            all_jobs.extend(fut.result())

    if not all_jobs:
        return _empty_df()

    rows = [j.to_dict() for j in all_jobs]
    df = pd.DataFrame(rows)

    # Drop exact URL duplicates while keeping first occurrence
    if "job_url" in df.columns:
        df = df.drop_duplicates(subset=["job_url"], keep="first")

    # Stable column order
    preferred = [
        "id",
        "title",
        "company",
        "country",
        "city",
        "location",
        "is_remote",
        "employment_type",
        "salary_min",
        "salary_max",
        "currency",
        "experience_level",
        "skills",
        "site_name",
        "job_url",
        "description",
        "date_posted",
        "deadline",
    ]
    ordered = [c for c in preferred if c in df.columns] + [
        c for c in df.columns if c not in preferred
    ]
    return df[ordered].reset_index(drop=True)


def _empty_df() -> pd.DataFrame:
    return pd.DataFrame(
        columns=[
            "id",
            "title",
            "company",
            "country",
            "city",
            "location",
            "is_remote",
            "employment_type",
            "salary_min",
            "salary_max",
            "currency",
            "experience_level",
            "skills",
            "site_name",
            "job_url",
            "description",
            "date_posted",
            "deadline",
        ]
    )
