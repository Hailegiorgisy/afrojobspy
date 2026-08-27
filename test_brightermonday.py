import logging
from afrojobspy.scrapers.brightermonday import BrighterMondayScraper

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

def test_brightermonday():
    print("=" * 60)
    print("🧪 TESTING BRIGHTERMONDAY SCRAPER ISOLATION")
    print("=" * 60)

    scraper = BrighterMondayScraper()
    jobs = scraper.scrape(search_term="", results_wanted=5)

    print(f"\nTotal jobs retrieved from BrighterMonday: {len(jobs)}")
    print("-" * 60)

    if jobs:
        for idx, job in enumerate(jobs, 1):
            print(f"{idx}. {job.title}")
            print(f"   Company:  {job.company}")
            print(f"   Location: {job.location}")
            print(f"   URL:      {job.job_url}")
            print("-" * 60)
    else:
        print("❌ No jobs returned.")

if __name__ == "__main__":
    test_brightermonday()