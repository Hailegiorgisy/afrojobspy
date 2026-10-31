---
title: 'AfroJobsPy: A Concurrent Python Library for Aggregating Job Listings from African Employment Platforms'
tags:
  - Python
  - web scraping
  - labour market
  - Africa
  - Ethiopia
  - job boards
  - open source
  - public health workforce
authors:
  - name: Hailegiorgis Yirgu Habtie
    orcid: 0000-0002-3801-1560
    affiliation: "1"
affiliations:
  - name: EASEAFRICA, Addis Ababa, Ethiopia
    index: 1
date: 31 October 2026
bibliography: paper.bib
---

# Summary

Access to structured, up-to-date job-market data is essential for labour economists, public-health workforce planners, career platforms and job seekers. While mature open-source scrapers exist for global boards such as LinkedIn, Indeed and Glassdoor, the majority of vacancies in African labour markets are advertised on local and regional portals that these tools do not cover. **AfroJobsPy** is a lightweight, concurrent Python library that fills this gap. It provides a unified interface to scrape and normalise job postings from eighteen African and pan-African employment platforms spanning East, West, Southern and North Africa as well as continental institutions (African Union, ReliefWeb, UN system). Results are returned as a pandas DataFrame with a consistent schema, enabling immediate downstream analysis, matching or archival.

# Statement of need

African job markets are highly fragmented. A data scientist in Addis Ababa, a nurse in Nairobi or a policy analyst in Accra must consult multiple national portals, NGO boards and Telegram channels. Existing libraries such as python-jobspy [@jobspy] focus on Western and a few Asian boards; specialised African tools are either single-country bots or closed commercial services. Researchers studying skills gaps, youth employment or health-workforce distribution therefore lack a reproducible, open data-collection layer.

AfroJobsPy addresses this need by:

1. Supplying **dedicated adapters** for high-traffic local boards (EthioJobs, Afriwork, BrighterMonday, Jobberman, Wuzzuf, CareerJunction, etc.).
2. Offering **geographic filters** (country or economic region) so that a single call can target Ethiopia, East Africa or the whole continent.
3. Returning a **standardised schema** (title, company, location, salary bounds, skills, deadlines, source URL) suitable for statistical analysis and machine-learning pipelines.
4. Running adapters **concurrently** with isolation of failures, exponential-backoff retries and optional proxy rotation.

The library is intended for researchers, labour-market observatories, public-health programme managers, career-service developers and open-data practitioners.

# Design and implementation

AfroJobsPy follows a classic adapter pattern. An abstract `BaseScraper` manages HTTP sessions, realistic browser headers, optional proxy pools and retry logic with exponential backoff. Each concrete adapter implements a single `scrape(search_term, location, results_wanted)` method that returns a list of `JobPost` Pydantic models. A central registry maps short site keys to adapter classes.

The public entry point `scrape_jobs()` resolves the requested set of sites from three optional filters (explicit site list, country, or region), launches the selected adapters inside a `ThreadPoolExecutor`, concatenates the results, removes exact URL duplicates and returns a pandas DataFrame. A command-line interface (`afrojobspy search` / `afrojobspy list-sites`) exposes the same functionality for non-programmers and shell pipelines.

Key design decisions:

- **Minimal dependencies** – requests, BeautifulSoup4, Pydantic v2, pandas.
- **Failure isolation** – a broken or blocked site never aborts the whole run.
- **Extensibility** – adding a new board requires only a new module and a one-line registry entry.
- **Ethical defaults** – documentation emphasises respect for robots.txt, rate limits and site terms of service.

# Example usage

```python
from afrojobspy import scrape_jobs

df = scrape_jobs(
    search_term="Public Health",
    region="east_africa",
    results_wanted=20,
    max_workers=6,
)
print(df[["title", "company", "country", "site_name"]].head())
```

```bash
afrojobspy search -q "Software Engineer" -c ethiopia -n 15 -o jobs.csv
```

# Research applications

AfroJobsPy can serve as the data-collection layer for:

- Skills-gap and occupational-demand studies at national or regional scale.
- Health-workforce and public-health vacancy monitoring.
- Evaluation of formal versus informal recruitment channels (web portals vs Telegram).
- Construction of longitudinal vacancy indices when run on a schedule.
- Training sets for job-matching or recommendation models focused on African markets.

# Limitations and future work

Scrapers that rely on HTML structure are inherently brittle; site redesigns will require maintenance. Not every adapter yet extracts salary, skills or full descriptions with equal completeness. Future releases will prioritise official APIs where available, richer structured extraction (including optional LLM post-processing), broader coverage of Francophone and Lusophone boards, and scheduled archival snapshots.

# Acknowledgements

The author thanks the open-source community whose patterns (especially the JobSpy family of projects) informed the overall architecture, the maintainers of the African job portals that publish public listings, and EASEAFRICA (https://www.easeafrica.org.et) for institutional support.

# References
