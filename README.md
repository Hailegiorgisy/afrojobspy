# AfroJobsPy 🌍💼

AfroJobsPy is a lightweight and modular Python library designed to scrape job listings from leading African employment platforms.

## Supported Job Boards
* **EthioJobs** (`ethiojobs`)
* **Fuzu** (`fuzu`)
* **GeezJobs** (`geezjobs`)
* **Jobberman** (`jobberman`)
* **JobWebZambia** (`jobwebzambia`)
* **MyJobMag** (`myjobmag`)
* **Rekrute** (`rekrute`)
* **TunisiaTravail** (`tunisiatravail`)

## Installation

Clone the repository and install it locally in editable mode:

```bash
pip install -e .

from afrojobspy.scrapers.ethiojobs import EthioJobsScraper

scraper = EthioJobsScraper()
jobs = scraper.scrape(search_term="Developer", results_wanted=5)

for job in jobs:
    print(f"{job.title} at {job.company} -> {job.job_url}")