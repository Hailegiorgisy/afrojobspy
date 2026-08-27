import logging
from afrojobspy.scrapers.afriwork import AfriworkScraper

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

def test_afriwork():
    print("=" * 60)
    print("🧪 TESTING AFRIWORK SCRAPER ISOLATION")
    print("=" * 60)

    scraper = AfriworkScraper()
    jobs = scraper.scrape(search_term="", results_wanted=5)

    print(f"\nTotal jobs retrieved from Afriwork: {len(jobs)}")
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
    test_afriwork()