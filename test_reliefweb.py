from afrojobspy.scrapers.reliefweb import ReliefWebScraper

scraper = ReliefWebScraper()
print("Testing ReliefWeb HTML Scraper...")
jobs = scraper.scrape(search_term="Python", location="", results_wanted=3)

print(f"Successfully fetched {len(jobs)} jobs from ReliefWeb!")
for job in jobs:
    print(f"- {job.title} at {job.company} ({job.job_url})")