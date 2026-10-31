import re
import logging
from typing import List, Optional
from bs4 import BeautifulSoup
from afrojobspy.scrapers.base import BaseScraper
from afrojobspy.models import JobPost

logger = logging.getLogger(__name__)

class TelegramJobsScraper(BaseScraper):
    """
    Scraper for public Telegram employment channels in East Africa/Ethiopia.
    Uses public channel web views (https://t.me/s/<channel>) without requiring API tokens.
    Default channels include 'afriwork' and 'tikvahjobs'.
    """

    DEFAULT_CHANNELS = ["afriwork", "tikvahjobs"]

    def __init__(self, proxies: Optional[List[str]] = None, channels: Optional[List[str]] = None):
        super().__init__(proxies=proxies)
        self.channels = channels or self.DEFAULT_CHANNELS

    def scrape(
        self,
        search_term: str = "",
        location: str = "",
        results_wanted: int = 10,
        **kwargs
    ) -> List[JobPost]:
        jobs: List[JobPost] = []
        seen_urls = set()

        for channel in self.channels:
            url = f"https://t.me/s/{channel}"
            resp = self._safe_get(url)
            if not resp:
                continue

            soup = BeautifulSoup(resp.text, "html.parser")
            messages = soup.select("div.tgme_widget_message_wrap")

            # Process latest messages first
            for msg_wrap in reversed(messages):
                text_elem = msg_wrap.select_one("div.tgme_widget_message_text")
                if not text_elem:
                    continue

                full_text = text_elem.get_text("\n", strip=True)
                lines = [l.strip() for l in full_text.split("\n") if l.strip()]
                if not lines:
                    continue

                # Heuristic for title: first substantive line
                raw_title = lines[0]
                if len(raw_title) > 100:
                    raw_title = raw_title[:97] + "..."

                if search_term and search_term.lower() not in full_text.lower():
                    continue

                # Message URL
                time_link = msg_wrap.select_one("a.tgme_widget_message_date")
                job_url = time_link.get("href", "") if time_link else url
                if job_url in seen_urls:
                    continue
                seen_urls.add(job_url)

                # Company heuristic: line starting with Company/Organization or channel name
                company = f"Telegram @{channel}"
                for line in lines:
                    if re.match(r"(?i)^(company|organization|employer|ድርጅት)\s*[:\-]\s*", line):
                        company = re.sub(r"(?i)^(company|organization|employer|ድርጅት)\s*[:\-]\s*", "", line).strip()
                        break

                # Deadline heuristic
                deadline = None
                for line in lines:
                    if re.match(r"(?i)^(deadline|closing date|ማብቂያ)\s*[:\-]\s*", line):
                        deadline = re.sub(r"(?i)^(deadline|closing date|ማብቂያ)\s*[:\-]\s*", "", line).strip()
                        break

                date_posted = time_link.get_text(strip=True) if time_link else None

                jobs.append(JobPost(
                    title=self._clean_text(raw_title),
                    company=self._clean_text(company),
                    country="Ethiopia",
                    location=location or "Ethiopia",
                    site_name=f"telegram_{channel}",
                    job_url=job_url,
                    description=full_text[:500],
                    deadline=deadline,
                    date_posted=date_posted
                ))

                if len(jobs) >= results_wanted:
                    return jobs

        return jobs
