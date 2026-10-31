from afrojobspy.scrapers.base import BaseScraper

# Try initializing a dummy child class
class DummyScraper(BaseScraper):
    def scrape(self, search_term: str, location: str, results_wanted: int):
        return []

try:
    scraper = DummyScraper()
    print("BaseScraper and inheritance pattern successfully validated!")
    print(f"Session headers loaded: {dict(scraper.session.headers)}")
except Exception as e:
    print(f"Error: {e}")