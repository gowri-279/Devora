"""
Developer Twin evaluation mapping.

This module is intentionally limited to the Knowledge Engine's
responsibility:

1. Receive an already-produced structured evaluation.
2. Inspect the specific developer's existing Twin skill keys.
3. Map evaluation categories to an existing Twin skill where possible.
4. Never create new Twin skill keys from assessment categories.
5. Apply only valid mapped scores through developer_twin.update_twin_scores().

This module does NOT:
- call IBM Bob / watsonx
- evaluate free-text answers
- generate assessment questions
- calculate AI scores

The AI/evaluator service is responsible for producing the evaluation.
The Knowledge Engine is responsible only for safely applying it to
the Developer Twin.
"""

from typing import Optional

from app.developer_twin import get_twin, update_twin_scores


# Candidate Twin skill keys for known evaluation categories.
#
# Candidates are checked in order. The first candidate that already
# exists in THIS developer's Twin is used.
#
# Example:
#   evaluation category = "backend_api"
#   Twin skills = {"python": 90, "fastapi": 50, "mongodb": 40}
#   -> maps to "fastapi"
#
# If none of the candidates exists, the category remains unmapped.
CONDITIONAL_MAPPING = {
    "authentication": [
        "authentication",
    ],
    "backend_api": [
        "fastapi",
        "rest_apis",
    ],
    "database": [
        "mongodb",
        "sql",
        "postgresql",
        "database",
    ],
    "debugging_problem_solving": [
        "debugging",
    ],
    "architecture": [
        "architecture",
    ],
}


def _normalise_skill_key(value: object) -> str:
    """Normalize a skill/category key for comparison."""
    return str(value).strip().lower()


def _extract_score(area: object) -> Optional[float]:
    """
    Extract a numeric score from a knowledge-area value.

    Supported input:
        {"score": 75}

    Also accepts a direct numeric value for defensive compatibility:
        75
    """
    if isinstance(area, dict):
        area = area.get("score")

    try:
        return float(area)
    except (TypeError, ValueError):
        return None


def _find_existing_twin_skill(
    category: str,
    twin_skills: dict,
) -> Optional[str]:
    """
    Find an existing Twin skill that the evaluation category can update.

    Matching is always against the actual keys already present in the
    developer's Twin.

    No new key is ever created here.
    """
    normalized_existing = {
        _normalise_skill_key(skill): skill
        for skill in twin_skills.keys()
    }

    normalized_category = _normalise_skill_key(category)

    # Known conditional mapping.
    candidates = CONDITIONAL_MAPPING.get(
        normalized_category,
        [normalized_category],
    )

    for candidate in candidates:
        normalized_candidate = _normalise_skill_key(candidate)

        if normalized_candidate in normalized_existing:
            return normalized_existing[normalized_candidate]

    return None


def map_evaluation_to_twin_updates(
    knowledge_areas: dict,
    twin_skills: dict,
) -> tuple[dict, dict, list]:
    """
    Map evaluation knowledge areas onto existing Twin skills.

    Returns:
        (
            updates,
            applied_mapping,
            unmapped_categories,
        )

    `updates`:
        {
            "fastapi": 78.0,
            "mongodb": 55.0
        }

    `applied_mapping`:
        {
            "backend_api": "fastapi",
            "database": "mongodb"
        }

    `unmapped_categories`:
        [
            "architecture"
        ]

    A category is considered unmapped when no corresponding skill
    already exists in the developer's Twin.
    """
    updates = {}
    applied_mapping = {}
    unmapped_categories = []

    if not isinstance(knowledge_areas, dict):
        return updates, applied_mapping, unmapped_categories

    twin_skills = twin_skills or {}

    for category, area in knowledge_areas.items():
        category_key = _normalise_skill_key(category)

        twin_skill = _find_existing_twin_skill(
            category_key,
            twin_skills,
        )

        if twin_skill is None:
            unmapped_categories.append(category)
            continue

        score = _extract_score(area)

        if score is None:
            continue

        updates[twin_skill] = max(
            0.0,
            min(100.0, score),
        )

        applied_mapping[category] = twin_skill

    return (
        updates,
        applied_mapping,
        unmapped_categories,
    )


def apply_evaluation_to_twin(
    developer_id: str,
    project_id: str,
    evaluation: dict,
) -> dict:
    """
    Safely apply an evaluation to an existing Developer Twin.

    Important:
    - If the Twin does not exist, nothing is created.
    - If an evaluation category has no matching existing Twin skill,
      it remains unmapped.
    - Only existing Twin keys can be updated.
    """
    twin = get_twin(
        developer_id=developer_id,
        project_id=project_id,
    )

    if not twin:
        return {
            "status": "twin_not_found",
            "developer_id": developer_id,
            "project_id": project_id,
            "updated_twin": None,
            "applied_mapping": {},
            "unmapped_categories": list(
                (evaluation or {}).get("knowledge_areas", {}).keys()
            ),
        }

    twin_skills = twin.get("skills", {}) or {}

    knowledge_areas = (
        (evaluation or {}).get("knowledge_areas", {})
    )

    (
        updates,
        applied_mapping,
        unmapped_categories,
    ) = map_evaluation_to_twin_updates(
        knowledge_areas=knowledge_areas,
        twin_skills=twin_skills,
    )

    if updates:
        updated_twin = update_twin_scores(
            developer_id=developer_id,
            project_id=project_id,
            knowledge_scores=updates,
        )
    else:
        updated_twin = twin

    return {
        "status": "updated" if updates else "no_matching_skills",
        "developer_id": developer_id,
        "project_id": project_id,
        "updated_twin": updated_twin,
        "applied_mapping": applied_mapping,
        "unmapped_categories": unmapped_categories,
    }

