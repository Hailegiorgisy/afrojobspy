import logging
from typing import List, Optional
import pandas as pd

from afrojobspy.models import JobPost
from afrojobspy.scrapers.myjobmag import MyJobMagScraper
from afrojobspy.scrapers.jobberman import JobbermanScraper
from afrojobspy.scrapers.ethiojobs import EthiojobsScraper
from afrojobspy.scrapers.reliefweb import ReliefWebScraper
from afrojobspy.scrapers.unjobs import UNJobsScraper

logger = logging.getLogger(__name__)

def scrape_jobs(
    search_term: str,
    location: str = "",
    results_wanted: int = 10,
    sites: Optional[List[str]] = None,
    proxies: Optional[List[str]] = None
) -> pd.DataFrame:
    """
    Orchestrator function to scrape job posts across multiple African and international 
    job platforms and return them as a consolidated Pandas DataFrame.

    :param search_term: Keyword to search for (e.g., "Python", "Data Scientist")
    :param location: Location filter (e.g., "Ethiopia", "Kenya", or blank)
    :param results_wanted: Total number of jobs desired per platform
    :param sites: List of sites to scrape (e.g., ["myjobmag", "reliefweb", "ethiojobs"]). Defaults to all.
    :param proxies: Optional list of proxy strings.
    :return: Pandas DataFrame containing consolidated job posts.
    """
    all_jobs: List[JobPost] = []
    
    # Map all available scraper classes
    available_scrapers = {
        "myjobmag": MyJobMagScraper,
        "jobberman": JobbermanScraper,
        "ethiojobs": EthiojobsScraper,
        "reliefweb": ReliefWebScraper,
        "unjobs": UNJobsScraper
    }
    
    # Determine which sites to query
    if sites is None:
        target_sites = list(available_scrapers.keys())
    else:
        target_sites = [s.lower() for s in sites if s.lower() in available_scrapers]
        
    if not target_sites:
        logger.error("No valid scraping sites provided.")
        return pd.DataFrame()

    # Execute scrapers
    for site_name in target_sites:
        logger.info(f"Starting scrape on {site_name} for '{search_term}'...")
        try:
            scraper_cls = available_scrapers[site_name]
            scraper = scraper_cls(proxies=proxies)
            jobs = scraper.scrape(search_term=search_term, location=location, results_wanted=results_wanted)
            all_jobs.extend(jobs)
            logger.info(f"Successfully retrieved {len(jobs)} jobs from {site_name}.")
        except Exception as e:
            logger.error(f"Error running scraper for {site_name}: {e}")

    # Convert Pydantic models to a Pandas DataFrame
    if not all_jobs:
        logger.warning("No jobs found across any platform.")
        return pd.DataFrame(columns=["id", "title", "company", "location", "site_name", "job_url", "description", "date_posted"])

    data = [job.model_dump() for job in all_jobs]
    df = pd.DataFrame(data)
    
    # Drop potential duplicates based on job_url
    df.drop_duplicates(subset=["job_url"], inplace=True)
    df.reset_index(drop=True, inplace=True)
    
    return df