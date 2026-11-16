"""Abstract base scraper with resilient HTTP handling for African job boards."""

from __future__ import annotations

import logging
import random
import re
import time
from abc import ABC, abstractmethod
# Line 10
from typing import Any, Dict, List, Optional, Tuple, Union

import requests

from afrojobspy.models import JobPost

logger = logging.getLogger(__name__)

# Rotate among a small set of realistic desktop UAs to reduce trivial blocks
_USER_AGENTS = [
    (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) "
        "Version/17.4 Safari/605.1.15"
    ),
    (
        "Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/123.0.0.0 Safari/537.36"
    ),
    (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) "
        "Gecko/20100101 Firefox/124.0"
    ),
]


class BaseScraper(ABC):
    """
    Abstract base class for African job-board scrapers.

    Provides:
    - Session lifecycle and realistic browser headers
    - Optional proxy support (single or rotating list)
    - Exponential-backoff retries on transient network / 5xx errors
    - Text normalisation helpers
    """
# Lines 53–62
    DEFAULT_TIMEOUT: Tuple[int, int] = (5, 15)
    MAX_RETRIES = 3
    BACKOFF_BASE = 1.4  # seconds

    def __init__(
        self,
        proxies: Optional[List[str]] = None,
        timeout: Union[int, float, Tuple[int, int]] = DEFAULT_TIMEOUT,
        max_retries: int = MAX_RETRIES,
    ):
        self.session = requests.Session()
        self.timeout = timeout
        self.max_retries = max_retries
        self._proxy_pool: List[str] = list(proxies) if proxies else []
        self._proxy_idx = 0

        self.session.headers.update(
            {
                "User-Agent": random.choice(_USER_AGENTS),
                "Accept": (
                    "text/html,application/xhtml+xml,application/xml;q=0.9,"
                    "image/avif,image/webp,*/*;q=0.8"
                ),
                "Accept-Language": "en-US,en;q=0.9,am;q=0.8,fr;q=0.7,sw;q=0.6",
                "Accept-Encoding": "gzip, deflate",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "DNT": "1",
            }
        )
        self._apply_proxy()

    def _apply_proxy(self) -> None:
        """Set the current proxy from the pool (if any) on the session."""
        if not self._proxy_pool:
            self.session.proxies = {}
            return
        proxy_url = self._proxy_pool[self._proxy_idx % len(self._proxy_pool)]
        self.session.proxies = {"http": proxy_url, "https": proxy_url}

    def _rotate_proxy(self) -> None:
        """Advance to the next proxy in the pool."""
        if len(self._proxy_pool) > 1:
            self._proxy_idx = (self._proxy_idx + 1) % len(self._proxy_pool)
            self._apply_proxy()
            logger.debug(
                "[%s] Rotated proxy → %s",
                self.__class__.__name__,
                self.session.proxies.get("http"),
            )

    def _safe_get(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Optional[requests.Response]:
        """
        GET with exponential backoff and optional proxy rotation.

        Retries on connection errors, timeouts, and HTTP 429 / 5xx.
        """
        last_exc: Optional[Exception] = None

        for attempt in range(1, self.max_retries + 1):
            try:
                req_headers = dict(self.session.headers)
                if headers:
                    req_headers.update(headers)

                response = self.session.get(
                    url,
                    params=params,
                    headers=req_headers,
                    timeout=self.timeout,
                )

                if response.status_code == 200:
                    return response

                if response.status_code in (429, 500, 502, 503, 504):
                    logger.warning(
                        "[%s] HTTP %s for %s (attempt %d/%d)",
                        self.__class__.__name__,
                        response.status_code,
                        url,
                        attempt,
                        self.max_retries,
                    )
                    self._rotate_proxy()
                    time.sleep(self.BACKOFF_BASE ** attempt + random.uniform(0, 0.5))
                    continue

                logger.warning(
                    "[%s] Unexpected status %s for URL: %s",
                    self.__class__.__name__,
                    response.status_code,
                    url,
                )
                return None

            except requests.RequestException as exc:
                last_exc = exc
                logger.warning(
                    "[%s] Request failed (attempt %d/%d) for %s: %s",
                    self.__class__.__name__,
                    attempt,
                    self.max_retries,
                    url,
                    exc,
                )
                self._rotate_proxy()
                if attempt < self.max_retries:
                    time.sleep(self.BACKOFF_BASE ** attempt + random.uniform(0, 0.5))

        if last_exc:
            logger.error(
                "[%s] Exhausted retries for %s: %s",
                self.__class__.__name__,
                url,
                last_exc,
            )
        return None

    @staticmethod
    def _clean_text(text: Optional[str]) -> str:
        """Collapse whitespace and strip; return empty string for None/blank."""
        if not text:
            return ""
        return re.sub(r"\s+", " ", str(text)).strip()

    @abstractmethod
    def scrape(
        self,
        search_term: str = "",
        location: str = "",
        results_wanted: int = 10,
        **kwargs: Any,
    ) -> List[JobPost]:
        """Scrape the target board and return a list of normalised JobPost objects."""
        ...
