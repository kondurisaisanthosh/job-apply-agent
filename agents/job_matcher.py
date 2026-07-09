def calculate_match_score(job_title: str, job_text: str, resume_text: str, preferences: dict) -> int:
    score = 0

    combined_text = f"{job_title} {job_text}".lower()
    resume_text = resume_text.lower()

    target_titles = preferences.get("target_titles", [])
    required_keywords = preferences.get("required_keywords", [])
    locations = preferences.get("locations", [])

    # Title match
    for title in target_titles:
        title_lower = title.lower()

        if title_lower in combined_text:
            score += 30
        else:
            title_words = title_lower.split()
            for word in title_words:
                if word in combined_text:
                    score += 8

    # Skill match
    for keyword in required_keywords:
        keyword_lower = keyword.lower()

        if keyword_lower in combined_text:
            score += 10

        if keyword_lower in resume_text and keyword_lower in combined_text:
            score += 5

    # Location match
    for location in locations:
        if location.lower() in combined_text:
            score += 5

    return min(score, 100)