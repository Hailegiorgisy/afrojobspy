import logging
import pandas as pd
from typing import List, Optional

from afrojobspy.models import JobPost
from afrojobspy.scrapers.ethiojobs import EthiojobsScraper
from afrojobspy.scrapers.afriwork import AfriworkScraper
from afrojobspy.scrapers.aujobs import AUJobsScraper
from afrojobspy.scrapers.brightermonday import BrighterMondayScraper
from afrojobspy.scrapers.hahujobs import HahuJobsScraper
from afrojobspy.scrapers.geezjobs import GeezJobsScraper
from afrojobspy.models import JobPost
from afrojobspy.scrapers.ethiojobs import EthiojobsScraper
from afrojobspy.scrapers.geezjobs import GeezJobsScraper

__version__ = "0.1.0"

logger = logging.getLogger(__name__)

# Map site keys to their corresponding scraper classes
SCRAPER_REGISTRY = {
    "ethiojobs": EthiojobsScraper,
    "afriwork": AfriworkScraper,
    "au_jobs": AUJobsScraper,
    "brightermonday": BrighterMondayScraper,
    "hahujobs": HahuJobsScraper,
    "geezjobs": GeezJobsScraper,
}

def scrape_jobs(
    search_term: str = "",
    location: str = "",
    results_wanted: int = 10,
    sites: Optional[List[str]] = None,
    proxies: Optional[List[str]] = None
) -> pd.DataFrame:
    """
    Orchestrates job scraping across multiple African job platforms 
    and returns a consolidated pandas DataFrame.
    """
    if sites is None:
        sites = list(SCRAPER_REGISTRY.keys())

    all_jobs: List[JobPost] = []

    for site_key in sites:
        site_key = site_key.lower().strip()
        if site_key not in SCRAPER_REGISTRY:
            logger.warning(f"Unknown or unregistered site key: '{site_key}'. Skipping.")
            continue

        scraper_cls = SCRAPER_REGISTRY[site_key]
        try:
            logger.info(f"Initializing scraper for {site_key}...")
            scraper = scraper_cls(proxies=proxies)
            jobs = scraper.scrape(search_term=search_term, location=location, results_wanted=results_wanted)
            logger.info(f"Successfully scraped {len(jobs)} jobs from {site_key}.")
            all_jobs.extend(jobs)
        except Exception as e:
            logger.error(f"Error scraping {site_key}: {e}")

    # Convert JobPost dataclass/pydantic models to a list of dicts for pandas
    jobs_data = [job.model_dump() if hasattr(job, "model_dump") else job.__dict__ for job in all_jobs]
    
    if not jobs_data:
        return pd.DataFrame(columns=["id", "title", "company", "location", "site_name", "job_url", "description", "date_posted"])

    df = pd.DataFrame(jobs_data)
    
    # Drop exact duplicates if any URL repeats
    if "job_url" in df.columns:
        df = df.drop_duplicates(subset=["job_url"])

    return df