import yaml
from pathlib import Path

from agents.resume_parser import read_resume_text
from agents.job_matcher import calculate_match_score
from agents.job_analyzer import analyze_job
from agents.tracker import save_jobs_to_excel
from browser.playwright_runner import find_jobs_on_page


BASE_DIR = Path(__file__).resolve().parent


def load_yaml(path: Path) -> dict:
    with open(path, "r") as file:
        return yaml.safe_load(file)


def main():
    print("Reading resume...")
    resume_text = read_resume_text(BASE_DIR / "resume" / "resume.pdf")

    print("Loading preferences...")
    preferences = load_yaml(BASE_DIR / "config" / "preferences.yaml")

    print("Loading companies...")
    companies_config = load_yaml(BASE_DIR / "config" / "companies.yaml")

    matched_jobs = []

    for company in companies_config.get("companies", []):
        company_name = company["name"]
        careers_url = company["careers_url"]

        jobs = find_jobs_on_page(company_name, careers_url)

        for job in jobs:
            score = calculate_match_score(
                job_title=job["job_title"],
                job_text=job["job_text"],
                resume_text=resume_text,
                preferences=preferences
            )

            if score >= preferences.get("min_score", 20):
                analysis = analyze_job(
                    job_title=job["job_title"],
                    job_text=job["job_text"],
                    resume_text=resume_text,
                    preferences=preferences
                )

                matched_jobs.append({
                    "company": job["company"],
                    "job_title": job["job_title"],
                    "job_url": job["job_url"],
                    "match_score": score,
                    "matched_skills": analysis["matched_skills"],
                    "missing_skills": analysis["missing_skills"],
                    "fit_summary": analysis["fit_summary"],
                    "recommendation": analysis["recommendation"],
                    "status": "Found",
                    "applied_date": "",
                    "notes": ""
                })

    save_jobs_to_excel(matched_jobs, BASE_DIR / "data" / "applications.xlsx")


if __name__ == "__main__":
    main()