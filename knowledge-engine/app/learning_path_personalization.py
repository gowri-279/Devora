"""
Learning Path Personalization

Annotates existing learning-path modules with Developer Twin data.
Additive only: does NOT reorder modules, does NOT touch step numbering,
prerequisites, or repository-intelligence ranking. If no module matches
a given skill, that module is left completely untouched (no key added).
"""

from typing import Optional


# Light alias map so a skill name can match related module language even
# when the exact word doesn't literally appear (e.g. "authentication"
# should match a module titled "Security"). Any skill not listed here
# falls back to matching its own name directly as a substring.
SKILL_ALIASES = {
    "authentication": ["auth", "security", "oauth", "login"],
    "mongodb": ["mongodb", "mongo", "database"],
    "fastapi": ["fastapi", "api"],
    "rest_apis": ["api", "rest", "endpoint"],
    "git": ["git", "contribut", "workflow", "pull request"],
    "docker": ["docker", "container", "deploy"],
    "aws": ["aws", "cloud", "infrastructure"],
    "testing": ["test", "debug"],
}

# Reuses the same 0-49 / 50-79 / 80-100 rubric already established
# elsewhere in DEVORA's design (assessment scoring, team heatmap
# thresholds), for consistency across the app.
WEAK_THRESHOLD = 50
STRONG_THRESHOLD = 80


def _priority_for_score(score: float) -> str:
    if score >= STRONG_THRESHOLD:
        return "strong"
    if score >= WEAK_THRESHOLD:
        return "moderate"
    return "weak"


def _keywords_for_skill(skill: str) -> list:
    return SKILL_ALIASES.get(skill, [skill])


def _searchable_text(module: dict) -> str:
    parts = [
        module.get("title", "") or "",
        module.get("description", "") or "",
        module.get("purpose", "") or "",
        " ".join(module.get("sources", []) or []),
    ]
    return " ".join(parts).lower()


def personalize_modules(modules: list, twin: dict) -> dict:
    """
    Mutates `modules` in place, adding a "personalization" object to any
    module whose title/description/purpose/sources match one of the
    developer's declared skills.

    If a module matches multiple skills, the WEAKEST matching skill wins
    (most actionable signal for "why prioritize this").

    Returns a summary dict for the top-level "personalization_summary"
    field - not attached to individual modules.
    """
    skills = twin.get("skills", {}) if twin else {}

    weak_skills, moderate_skills, strong_skills = [], [], []
    for skill, score in skills.items():
        bucket = _priority_for_score(score)
        if bucket == "weak":
            weak_skills.append(skill)
        elif bucket == "moderate":
            moderate_skills.append(skill)
        else:
            strong_skills.append(skill)

    annotated_count = 0

    for module in modules:
        text = _searchable_text(module)

        best_skill: Optional[str] = None
        best_score: Optional[float] = None

        for skill, score in skills.items():
            keywords = _keywords_for_skill(skill)
            if any(kw in text for kw in keywords):
                if best_score is None or score < best_score:
                    best_skill = skill
                    best_score = score

        if best_skill is not None:
            module["personalization"] = {
                "related_skill": best_skill,
                "developer_familiarity": best_score,
                "priority": _priority_for_score(best_score),
                "reason": (
                    f"Matches your declared skill '{best_skill}' "
                    f"({best_score:.0f}/100)."
                ),
            }
            annotated_count += 1

    return {
        "developer_id": twin.get("developer_id"),
        "weak_skills": weak_skills,
        "moderate_skills": moderate_skills,
        "strong_skills": strong_skills,
        "modules_personalized": annotated_count,
    }