import logging
from afrojobspy.scrapers.addisjobs import AddisJobsScraper

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

def test_addisjobs():
    print("=" * 60)
    print("🧪 TESTING ADDIS JOBS SCRAPER ISOLATION")
    print("=" * 60)
    scraper = AddisJobsScraper()
    jobs = scraper.scrape(results_wanted=5)
    print(f"Total jobs: {len(jobs)}")
    for j in jobs:
        print(f"- {j.title} ({j.job_url})")

if __name__ == "__main__":
    test_addisjobs()