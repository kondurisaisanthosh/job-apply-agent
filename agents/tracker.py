from pathlib import Path
import pandas as pd


def save_jobs_to_excel(jobs: list, output_path: str = "data/applications.xlsx") -> None:
    Path("data").mkdir(exist_ok=True)

    columns = [
        "company",
        "job_title",
        "job_url",
        "match_score",
        "matched_skills",
        "missing_skills",
        "fit_summary",
        "recommendation",
        "status",
        "applied_date",
        "notes"
    ]

    df = pd.DataFrame(jobs)

    if df.empty:
        df = pd.DataFrame(columns=columns)
    else:
        for column in columns:
            if column not in df.columns:
                df[column] = ""

        df = df[columns]
        df = df.sort_values(by=["match_score"], ascending=False)

    df.to_excel(output_path, index=False)

    print(f"Saved {len(df)} jobs to {output_path}")