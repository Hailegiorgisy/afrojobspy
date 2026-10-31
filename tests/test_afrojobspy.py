"""Unit tests for AfroJobsPy core API (no live network required)."""

from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch

import pandas as pd

from afrojobspy import SCRAPER_REGISTRY, __version__, list_sites, scrape_jobs
from afrojobspy.models import ALL_SITE_KEYS, COUNTRY_SITES, REGION_MAP, JobPost
from afrojobspy.scrapers.base import BaseScraper


class TestModels(unittest.TestCase):
    def test_jobpost_required_fields(self):
        job = JobPost(
            title="Software Engineer",
            site_name="ethiojobs",
            job_url="https://example.com/job/1",
        )
        self.assertEqual(job.title, "Software Engineer")
        self.assertTrue(job.id)
        d = job.to_dict()
        self.assertIn("title", d)
        self.assertIn("job_url", d)

    def test_jobpost_rejects_empty_title(self):
        with self.assertRaises(Exception):
            JobPost(title="  ", site_name="x", job_url="https://x.com")

    def test_region_and_country_maps(self):
        self.assertIn("east_africa", REGION_MAP)
        self.assertIn("ethiopia", COUNTRY_SITES)
        self.assertTrue(len(ALL_SITE_KEYS) >= 10)


class TestRegistry(unittest.TestCase):
    def test_registry_populated(self):
        self.assertGreaterEqual(len(SCRAPER_REGISTRY), 15)
        for key, cls in SCRAPER_REGISTRY.items():
            self.assertTrue(issubclass(cls, BaseScraper), msg=key)

    def test_list_sites(self):
        cat = list_sites()
        self.assertIn("sites", cat)
        self.assertIn("countries", cat)
        self.assertIn("regions", cat)
        self.assertEqual(cat["version"], __version__)


class TestScrapeJobsAPI(unittest.TestCase):
    def test_empty_sites_returns_empty_df(self):
        df = scrape_jobs(sites=[])
        self.assertIsInstance(df, pd.DataFrame)
        self.assertTrue(df.empty)
        for col in ("id", "title", "company", "site_name", "job_url"):
            self.assertIn(col, df.columns)

    def test_unknown_site_skipped(self):
        df = scrape_jobs(sites=["nonexistent_board_xyz"])
        self.assertTrue(df.empty)

    @patch.object(SCRAPER_REGISTRY["ethiojobs"], "scrape", autospec=True)
    def test_single_site_mock(self, mock_scrape):
        mock_scrape.return_value = [
            JobPost(
                title="Test Role",
                company="Acme",
                site_name="ethiojobs",
                job_url="https://example.com/1",
                country="Ethiopia",
            )
        ]
        # We still need to instantiate; patch the class method after construction is harder.
        # Instead patch the worker path by temporarily replacing the registry entry.
        original = SCRAPER_REGISTRY["ethiojobs"]

        class Stub(BaseScraper):
            def scrape(self, search_term="", location="", results_wanted=10, **kwargs):
                return [
                    JobPost(
                        title="Test Role",
                        company="Acme",
                        site_name="ethiojobs",
                        job_url="https://example.com/1",
                        country="Ethiopia",
                    )
                ]

        SCRAPER_REGISTRY["ethiojobs"] = Stub
        try:
            df = scrape_jobs(sites=["ethiojobs"], results_wanted=5, max_workers=1)
            self.assertEqual(len(df), 1)
            self.assertEqual(df.iloc[0]["title"], "Test Role")
        finally:
            SCRAPER_REGISTRY["ethiojobs"] = original

    def test_country_resolution(self):
        from afrojobspy import _resolve_sites

        sites = _resolve_sites(country="ethiopia")
        self.assertTrue(len(sites) >= 5)
        self.assertIn("ethiojobs", sites)

    def test_region_resolution(self):
        from afrojobspy import _resolve_sites

        sites = _resolve_sites(region="east_africa")
        self.assertTrue(len(sites) >= 8)


class TestBaseScraper(unittest.TestCase):
    def test_clean_text(self):
        self.assertEqual(BaseScraper._clean_text("  hello   world  "), "hello world")
        self.assertEqual(BaseScraper._clean_text(None), "")

    def test_proxy_assignment(self):
        class Dummy(BaseScraper):
            def scrape(self, **kwargs):
                return []

        s = Dummy(proxies=["http://127.0.0.1:8080"])
        self.assertEqual(s.session.proxies.get("http"), "http://127.0.0.1:8080")


if __name__ == "__main__":
    unittest.main()
