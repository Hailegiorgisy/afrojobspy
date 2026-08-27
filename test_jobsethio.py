import logging
from afrojobspy.scrapers.jobsethio import JobsEthioScraper

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

def test_jobsethio():
    print("=" * 60)
    print("🧪 TESTING JOBSETHIO SCRAPER ISOLATION")
    print("=" * 60)
    scraper = JobsEthioScraper()
    jobs = scraper.scrape(results_wanted=5)
    print(f"Total jobs: {len(jobs)}")
    for j in jobs:
        print(f"- {j.title} ({j.job_url})")

if __name__ == "__main__":
    test_jobsethio()