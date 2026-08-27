import logging
from afrojobspy.scrapers.careers24 import Careers24Scraper

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

def test_careers24():
    print("=" * 60)
    print("🧪 TESTING CAREERS24 SCRAPER ISOLATION")
    print("=" * 60)
    scraper = Careers24Scraper()
    jobs = scraper.scrape(results_wanted=5)
    print(f"Total jobs: {len(jobs)}")
    for j in jobs:
        print(f"- {j.title} | Company: {j.company} ({j.job_url})")

if __name__ == "__main__":
    test_careers24()