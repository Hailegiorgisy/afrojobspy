from afrojobspy.scrapers.myjobmag import MyJobMagScraper

scraper = MyJobMagScraper()
print("Testing MyJobMag Scraper connection...")
# Request 3 Python jobs in Kenya/remote just to test connectivity/parsing structure
jobs = scraper.scrape(search_term="Python", location="", results_wanted=3)

print(f"Successfully fetched {len(jobs)} jobs!")
for job in jobs:
    print(f"- {job.title} at {job.company} ({job.job_url})")