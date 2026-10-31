# AfroJobsPy 🌍💼

**AfroJobsPy** is a modular, concurrent Python library that aggregates job listings from major African employment platforms into a single normalised pandas DataFrame.

[![PyPI version](https://img.shields.io/pypi/v/afrojobspy.svg)](https://pypi.org/project/afrojobspy/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

---

## Why AfroJobsPy?

Global job scrapers (JobSpy, etc.) focus on LinkedIn, Indeed and Western boards. African labour markets are fragmented across dozens of local portals that these tools ignore. AfroJobsPy fills that gap with:

- **18 dedicated adapters** covering Ethiopia, Kenya, Uganda, Nigeria, Ghana, South Africa, Egypt and pan-African institutions
- **Concurrent execution** via `ThreadPoolExecutor`
- **Geographic filters** by country or economic region
- **Resilient HTTP layer** (exponential backoff, proxy rotation, realistic User-Agents)
- **Standardised schema** (Pydantic v2 → pandas)

---

## Supported Platforms

| Region | Country | Platform | Key |
| :--- | :--- | :--- | :--- |
| **East Africa** | Ethiopia | EthioJobs | `ethiojobs` |
| | Ethiopia | Afriwork | `afriwork` |
| | Ethiopia | HaHuJobs | `hahujobs` |
| | Ethiopia | GeezJobs | `geezjobs` |
| | Ethiopia | Dereja | `dereja` |
| | Ethiopia | AddisJobs | `addisjobs` |
| | Ethiopia | JobsEthio | `jobsethio` |
| | Ethiopia | Telegram channels | `telegram_jobs` |
| | Kenya / Uganda | BrighterMonday | `brightermonday` |
| | Kenya / Uganda | Fuzu | `fuzu` |
| **West Africa** | Nigeria / Ghana | Jobberman | `jobberman` |
| | Multi-country | MyJobMag | `myjobmag` |
| **Southern Africa** | South Africa | CareerJunction | `careerjunction` |
| | South Africa | Careers24 | `careers24` |
| **North Africa** | Egypt | Wuzzuf | `wuzzuf` |
| **Pan-African** | Continental | African Union Jobs | `au_jobs` |
| | Humanitarian | ReliefWeb | `reliefweb` |
| | UN system | UN Jobs | `unjobs` |

---

## Installation

```bash
pip install afrojobspy
```

Or install from source:

```bash
git clone https://github.com/Hailegiorgisy/afrojobspy.git
cd afrojobspy
pip install -e ".[dev]"
```

**Requirements:** Python ≥ 3.9

---

## Quick Start (Python)

```python
from afrojobspy import scrape_jobs

# Search Ethiopia
df = scrape_jobs(
    search_term="Data Scientist",
    country="ethiopia",
    results_wanted=10,
)
print(df[["title", "company", "site_name", "job_url"]].head())

# East Africa, concurrent
df = scrape_jobs(
    search_term="Python Developer",
    region="east_africa",
    results_wanted=15,
    max_workers=6,
)
df.to_csv("east_africa_python.csv", index=False)

# Specific boards only
df = scrape_jobs(
    search_term="Project Manager",
    sites=["au_jobs", "brightermonday", "fuzu"],
    results_wanted=10,
)
```

---

## Command-Line Interface

```bash
# Catalogue of sites / countries / regions
afrojobspy list-sites

# Search by country
afrojobspy search -q "Software Engineer" -c ethiopia -n 15 -o ethiopia_tech.csv

# Search by region
afrojobspy search -q "Public Health" -r east_africa -o health_jobs.json

# Specific sites
afrojobspy search -q "Nurse" -s ethiojobs,hahujobs,geezjobs -n 20
```

---

## Output Schema

| Field | Type | Description |
| :--- | :--- | :--- |
| `id` | str | UUIDv4 |
| `title` | str | Job title |
| `company` | str | Employer name |
| `country` | str | ISO-style country name |
| `city` | str | City when available |
| `location` | str | Free-form location |
| `is_remote` | bool | Remote flag |
| `employment_type` | str | full_time / contract / … |
| `salary_min` / `salary_max` | float | Compensation bounds |
| `currency` | str | Currency code |
| `experience_level` | str | entry / mid / senior |
| `skills` | list[str] | Extracted skills |
| `site_name` | str | Origin platform key |
| `job_url` | str | Direct listing URL |
| `description` | str | Summary / excerpt |
| `date_posted` | str | Publication date |
| `deadline` | str | Application deadline |

---

## Design Notes

- **Adapter pattern** – each board implements `BaseScraper.scrape()`. Adding a new site requires only a new module and a one-line registry entry.
- **Resilience** – exponential backoff on 429/5xx and connection errors; optional rotating proxy pool; randomised User-Agent.
- **Isolation** – a failing adapter never aborts the whole run; results from healthy sites are still returned.
- **Ethics** – respect `robots.txt` and site Terms of Service; prefer official APIs when available; use rate-limiting and identify your bot.

---

## Development

```bash
pip install -e ".[dev]"
pytest -v
```

---

## Citation

If you use AfroJobsPy in research, please cite:

```bibtex
@software{habtie_afrojobspy_2026,
  author = {Habtie, Hailegiorgis Yirgu},
  title  = {AfroJobsPy: Concurrent Job Scraping for African Labour Markets},
  year   = {2026},
  url    = {https://github.com/Hailegiorgisy/afrojobspy},
  version = {0.2.0}
}
```

---

## License

MIT License © Hailegiorgis Yirgu Habtie
