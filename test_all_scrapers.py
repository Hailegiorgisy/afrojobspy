import logging
from afrojobspy.scrapers.ethiojobs import EthiojobsScraper
from afrojobspy.scrapers.afriwork import AfriworkScraper
from afrojobspy.scrapers.aujobs import AUJobsScraper
from afrojobspy.scrapers.brightermonday import BrighterMondayScraper
from afrojobspy.scrapers.hahujobs import HahuJobsScraper
from afrojobspy.scrapers.geezjobs import GeezJobsScraper

# Suppress excessive debug logs to keep output clean
logging.basicConfig(level=logging.WARNING)

def run_diagnostic():
    print("=" * 70)
    print("🔍 RUNNING COMPREHENSIVE AFROJOBSPY SCRAPER DIAGNOSTIC")
    print("=" * 70)
    
    # Map friendly names to their respective scraper instances
    scrapers_to_test = {
       
        "Afriwork": AfriworkScraper(),
        "AU Jobs": AUJobsScraper(),
        "BrighterMonday": BrighterMondayScraper(),
        "HaHuJobs": HahuJobsScraper(),
        
    }

    for name, scraper in scrapers_to_test.items():
        print(f"\n🚀 Testing scraper: [{name}]")
        try:
            jobs = scraper.scrape(search_term="", results_wanted=3)
            
            if jobs:
                print(f"   ✅ SUCCESS: Retrieved {len(jobs)} jobs!")
                for idx, job in enumerate(jobs[:2], 1):
                    print(f"      {idx}. {job.title} at {job.company}")
                    print(f"         URL: {job.job_url}")
            else:
                print(f"   ⚠️ WARNING: Returned 0 jobs. (Selectors or page structure may need updating)")
                
        except Exception as e:
            print(f"   ❌ ERROR: Failed with exception -> {e}")
            
    print("\n" + "=" * 70)
    print("✨ Diagnostic test run complete!")
    print("=" * 70)

if __name__ == "__main__":
    run_diagnostic()