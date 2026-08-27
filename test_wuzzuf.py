import logging
from afrojobspy.scrapers.wuzzuf import WuzzufScraper

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

def test_wuzzuf():
    print("=" * 60)
    print("🧪 TESTING WUZZUF SCRAPER ISOLATION")
    print("=" * 60)
    scraper = WuzzufScraper()
    jobs = scraper.scrape(results_wanted=5)
    print(f"Total jobs: {len(jobs)}")
    for j in jobs:
        print(f"- {j.title} | Company: {j.company} ({j.job_url})")

if __name__ == "__main__":
    test_wuzzuf()