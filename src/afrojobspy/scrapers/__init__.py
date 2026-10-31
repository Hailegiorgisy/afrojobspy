"""Scraper adapters for African job boards."""

from afrojobspy.scrapers.base import BaseScraper
from afrojobspy.scrapers.ethiojobs import EthiojobsScraper
from afrojobspy.scrapers.afriwork import AfriworkScraper
from afrojobspy.scrapers.hahujobs import HahuJobsScraper
from afrojobspy.scrapers.geezjobs import GeezJobsScraper
from afrojobspy.scrapers.dereja import DerejaScraper
from afrojobspy.scrapers.addisjobs import AddisJobsScraper
from afrojobspy.scrapers.jobsethio import JobsEthioScraper
from afrojobspy.scrapers.telegram_jobs import TelegramJobsScraper
from afrojobspy.scrapers.brightermonday import BrighterMondayScraper
from afrojobspy.scrapers.fuzu import FuzuScraper
from afrojobspy.scrapers.jobberman import JobbermanScraper
from afrojobspy.scrapers.myjobmag import MyJobMagScraper
from afrojobspy.scrapers.careerjunction import CareerJunctionScraper
from afrojobspy.scrapers.careers24 import Careers24Scraper
from afrojobspy.scrapers.wuzzuf import WuzzufScraper
from afrojobspy.scrapers.aujobs import AUJobsScraper
from afrojobspy.scrapers.reliefweb import ReliefWebScraper
from afrojobspy.scrapers.unjobs import UNJobsScraper

__all__ = [
    "BaseScraper",
    "EthiojobsScraper",
    "AfriworkScraper",
    "HahuJobsScraper",
    "GeezJobsScraper",
    "DerejaScraper",
    "AddisJobsScraper",
    "JobsEthioScraper",
    "TelegramJobsScraper",
    "BrighterMondayScraper",
    "FuzuScraper",
    "JobbermanScraper",
    "MyJobMagScraper",
    "CareerJunctionScraper",
    "Careers24Scraper",
    "WuzzufScraper",
    "AUJobsScraper",
    "ReliefWebScraper",
    "UNJobsScraper",
]
