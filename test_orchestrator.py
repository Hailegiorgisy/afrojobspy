from afrojobspy import scrape_jobs

print("Running Baseline Multi-Platform Orchestrator Test...")

# Pass an empty search term to see what's currently live across the boards
df = scrape_jobs(
    search_term="",
    results_wanted=3,
    sites=["ethiojobs", "au_jobs", "brightermonday", "hahujobs", "geezjobs"]
)

print(f"\nTotal unique jobs gathered across all platforms: {len(df)}")
print("=" * 80)

if not df.empty:
    print(df[["title", "company", "site_name"]].to_string(index=False))
    print("=" * 80)
    df.to_csv("all_africa_baseline_jobs.csv", index=False)
    print("\nSaved successfully to 'all_africa_baseline_jobs.csv'!")
else:
    print("No jobs returned. Check network or selectors.")