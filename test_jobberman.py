from afrojobspy.scrapers.jobberman import JobbermanScraper

scraper = JobbermanScraper()
print("Testing Jobberman Scraper connection...")
jobs = scraper.scrape(search_term="Python", location="", results_wanted=3)

print(f"Successfully fetched {len(jobs)} jobs from Jobberman!")
for job in jobs:
    print(f"- {job.title} at {job.company} ({job.job_url})")