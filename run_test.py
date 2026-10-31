from afrojobspy.scrapers.ethiojobs import EthiojobsScraper

def main():
    print("Initializing Ethiojobs Scraper...")
    scraper = EthiojobsScraper()
    
    jobs = scraper.scrape(search_term="", location="", results_wanted=5)
    
    print(f"\nSuccessfully fetched {len(jobs)} jobs from Ethiojobs!")
    for idx, job in enumerate(jobs, 1):
        print(f"{idx}. {job.title} at {job.company}")
        print(f"   URL: {job.job_url}")

if __name__ == "__main__":
    main()