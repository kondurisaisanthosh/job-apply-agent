def analyze_job(job_title: str, job_text: str, resume_text: str, preferences: dict) -> dict:
    combined_job_text = f"{job_title} {job_text}".lower()
    resume_text_lower = resume_text.lower()

    required_keywords = preferences.get("required_keywords", [])

    matched_skills = []
    missing_skills = []

    for skill in required_keywords:
        skill_lower = skill.lower()

        if skill_lower in combined_job_text:
            if skill_lower in resume_text_lower:
                matched_skills.append(skill)
            else:
                missing_skills.append(skill)

    match_count = len(matched_skills)
    missing_count = len(missing_skills)

    if match_count >= 6:
        recommendation = "High priority"
    elif match_count >= 3:
        recommendation = "Medium priority"
    else:
        recommendation = "Low priority"

    if matched_skills:
        fit_summary = (
            f"Good match because the role mentions {', '.join(matched_skills[:5])}."
        )
    else:
        fit_summary = "Weak match based on current resume keywords."

    if missing_skills:
        fit_summary += f" Missing or not visible in resume: {', '.join(missing_skills[:5])}."

    return {
        "matched_skills": ", ".join(matched_skills),
        "missing_skills": ", ".join(missing_skills),
        "fit_summary": fit_summary,
        "recommendation": recommendation
    }