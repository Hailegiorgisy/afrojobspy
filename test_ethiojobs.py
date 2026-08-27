from afrojobspy.scrapers.ethiojobs import EthiojobsScraper

scraper = EthiojobsScraper()
print("Testing Ethiojobs Scraper standalone...")
jobs = scraper.scrape(search_term="Python", location="", results_wanted=3)

print(f"Successfully fetched {len(jobs)} jobs from Ethiojobs!")
for job in jobs:
    print(f"- {job.title} at {job.company} ({job.job_url})")