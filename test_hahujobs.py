import logging
from afrojobspy.scrapers.hahujobs import HahuJobsScraper

# Enable debug logging to watch the JSON/HTML parsing steps in real-time
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

def test_hahujobs():
    print("=" * 60)
    print("🧪 TESTING HAHUJOBS SCRAPER ISOLATION")
    print("=" * 60)

    scraper = HahuJobsScraper()
    jobs = scraper.scrape(search_term="", results_wanted=5)

    print(f"\nTotal jobs retrieved from HaHuJobs: {len(jobs)}")
    print("-" * 60)

    if jobs:
        for idx, job in enumerate(jobs, 1):
            print(f"{idx}. {job.title}")
            print(f"   Company:  {job.company}")
            print(f"   Location: {job.location}")
            print(f"   URL:      {job.job_url}")
            print("-" * 60)
    else:
        print("❌ No jobs returned. The page structure might require an alternate endpoint.")

if __name__ == "__main__":
    test_hahujobs()