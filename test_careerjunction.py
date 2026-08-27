import logging
from afrojobspy.scrapers.careerjunction import CareerJunctionScraper

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

def test_careerjunction():
    print("=" * 60)
    print("🧪 TESTING CAREERJUNCTION SCRAPER ISOLATION")
    print("=" * 60)
    scraper = CareerJunctionScraper()
    jobs = scraper.scrape(results_wanted=5)
    print(f"Total jobs: {len(jobs)}")
    for j in jobs:
        print(f"- {j.title} | Company: {j.company} ({j.job_url})")

if __name__ == "__main__":
    test_careerjunction()