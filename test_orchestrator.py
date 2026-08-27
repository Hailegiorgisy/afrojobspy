from afrojobspy import scrape_jobs

print("Running 5-Platform AfroJobsPy Integration Test...")

df = scrape_jobs(
    search_term="Python",
    results_wanted=3,
    sites=["myjobmag", "jobberman", "ethiojobs", "reliefweb", "unjobs"]
)

print(f"\nTotal unique jobs gathered across all platforms: {len(df)}")
print("=" * 80)
if not df.empty:
    print(df[["title", "company", "site_name"]].to_string(index=False))
    print("=" * 80)
    df.to_csv("all_africa_python_jobs.csv", index=False)
    print("\nSaved successfully to 'all_africa_python_jobs.csv'!")
else:
    print("No jobs returned.")