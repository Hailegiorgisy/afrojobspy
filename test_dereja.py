import logging
from afrojobspy.scrapers.dereja import DerejaScraper

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

def test_dereja():
    print("=" * 60)
    print("🧪 TESTING DEREJA SCRAPER ISOLATION")
    print("=" * 60)
    scraper = DerejaScraper()
    jobs = scraper.scrape(results_wanted=5)
    print(f"Total jobs: {len(jobs)}")
    for j in jobs:
        print(f"- {j.title} ({j.job_url})")

if __name__ == "__main__":
    test_dereja()