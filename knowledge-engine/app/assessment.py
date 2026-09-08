"""
Step 3A — 5-Question Developer Knowledge Assessment.

Generates exactly 5 grounded questions, one per fixed category:
    1. architecture
    2. core_technical_understanding
    3. project_specific_implementation
    4. debugging_problem_solving
    5. self_assessment_gaps

Does NOT call an LLM. Every question is a deterministic template
interpolating ONLY real fields already produced by
generate_learning_path() (module title/description/purpose/sources) and
the Developer Twin's stored skills (via that same result's
personalization_summary, so no separate Twin lookup is needed here).
This is what guarantees requirement #3 from Step 3A: nothing is invented
that isn't already grounded Knowledge Engine data.

Fully stateless per Step 3A scope: nothing is persisted. The caller
(Backend/Bob evaluation step, later) is responsible for holding onto the
returned question metadata alongside the developer's answers.
"""

import uuid
from typing import Optional

from app.generate_learning_path import generate_learning_path


CATEGORY_ORDER = [
    "architecture",
    "core_technical_understanding",
    "project_specific_implementation",
    "debugging_problem_solving",
    "self_assessment_gaps",
]

# Keyword matching against module title/description/purpose, lowercased.
# self_assessment_gaps is intentionally absent - it's grounded in Twin
# data directly, not a specific module (see _build_self_assessment_question).
CATEGORY_KEYWORDS = {
    "architecture": ["architecture", "overview", "structure", "team foundations", "project overview"],
    "core_technical_understanding": ["security", "middleware", "dependencies", "compat", "openapi", "core", "fastapi"],
    "project_specific_implementation": ["api", "integration", "refund", "implementation", "business logic"],
    "debugging_problem_solving": ["bug", "debug", "troubleshoot", "kt", "incident"],
}

PRIORITY_RANK = {"weak": 0, "moderate": 1}  # anything else (strong / unmatched) falls through to 2


def _searchable_text(module: dict) -> str:
    parts = [
        module.get("title", "") or "",
        module.get("description", "") or "",
        module.get("purpose", "") or "",
    ]
    return " ".join(parts).lower()


def _module_matches_category(module: dict, category: str) -> bool:
    keywords = CATEGORY_KEYWORDS.get(category, [])
    text = _searchable_text(module)
    return any(kw in text for kw in keywords)


def _select_module_for_category(
    modules: list,
    category: str,
    used_steps: set,
) -> Optional[dict]:
    """
    Selection order, per the confirmed Step 3A plan:
      1. Category-keyword-matching modules, preferring weak > moderate >
         everything else, tiebroken by existing learning-path rank order.
      2. If no category match at all: next-best UNUSED module by
         existing rank order (honest fallback, no fact invention).
    """
    candidates = [m for m in modules if m.get("step") not in used_steps]
    if not candidates:
        return None

    keyword_matches = [m for m in candidates if _module_matches_category(m, category)]

    if keyword_matches:
        def sort_key(m):
            priority = (m.get("personalization") or {}).get("priority")
            priority_rank = PRIORITY_RANK.get(priority, 2)
            rank_order = modules.index(m)  # modules list is already in learning-path rank order
            return (priority_rank, rank_order)

        return sorted(keyword_matches, key=sort_key)[0]

    # Fallback: no category-specific module found. Next-best unused
    # module by existing rank order (modules list is pre-ordered).
    return candidates[0]


def _difficulty_for_module(module: dict) -> str:
    """Deterministic, based on real fields already on the module - not fabricated."""
    score = module.get("importance_score")
    if score is not None:
        if score >= 0.7:
            return "advanced"
        if score >= 0.4:
            return "intermediate"
        return "foundational"
    return "intermediate"  # doc-based modules have no importance_score


def _grounded_in_for_module(module: dict) -> str:
    return "repository_aware" if module.get("importance_score") is not None else "documentation_only"


def _source_files_for_module(module: dict) -> list:
    return module.get("source_files") or module.get("sources") or []


def _build_module_question(category: str, module: Optional[dict]) -> dict:
    if module is None:
        # Zero-module edge case: nothing to ground this question in at
        # all. Stay honest rather than inventing project-specific content.
        return {
            "question_id": str(uuid.uuid4()),
            "category": category,
            "question_text": (
                "No project documentation or repository information is currently "
                "available to generate a grounded question for this category."
            ),
            "tests_skill": None,
            "module_title": None,
            "module_step": None,
            "source_files": [],
            "difficulty": "foundational",
            "grounded_in": "none",
        }

    title = module.get("title", "this module")
    description = module.get("description") or module.get("purpose") or ""
    sources = _source_files_for_module(module)
    personalization = module.get("personalization") or {}
    tests_skill = personalization.get("related_skill")

    templates = {
        "architecture": (
            f"In your own words, explain the overall architecture and purpose of the "
            f"'{title}' component within this project, and why it matters for a new "
            f"developer working here."
        ),
        "core_technical_understanding": (
            f"Explain how the '{title}' module works and what problem it solves within "
            f"the codebase. Reference specific responsibilities covered in its source "
            f"files where relevant."
        ),
        "project_specific_implementation": (
            f"Describe how '{title}' is implemented specifically in this project - "
            f"what design decisions or conventions does this codebase follow here, "
            f"rather than a generic explanation?"
        ),
        "debugging_problem_solving": (
            f"If a developer ran into an issue related to '{title}', what debugging "
            f"steps or common pitfalls should they be aware of, based on what's "
            f"documented so far?"
        ),
    }

    question_text = templates.get(category, f"Describe your understanding of '{title}'.")
    if description:
        question_text += f" (Context: {description})"

    return {
        "question_id": str(uuid.uuid4()),
        "category": category,
        "question_text": question_text,
        "tests_skill": tests_skill,
        "module_title": title,
        "module_step": module.get("step"),
        "source_files": sources,
        "difficulty": _difficulty_for_module(module),
        "grounded_in": _grounded_in_for_module(module),
    }


def _build_self_assessment_question(personalization_summary: Optional[dict]) -> dict:
    """
    Grounded in the Developer Twin's own stored weak_skills - real data,
    not module content, and not invented. If no Twin/weak skills exist,
    falls back to an honest generic reflective prompt.
    """
    weak_skills = (personalization_summary or {}).get("weak_skills") or []

    if weak_skills:
        skills_list = ", ".join(weak_skills)
        question_text = (
            f"Reflecting on your own knowledge, which of these areas do you still feel "
            f"least confident about: {skills_list}? Explain specifically what you'd "
            f"want to learn more about and why."
        )
        grounded_in = "twin_self_assessment"
    else:
        question_text = (
            "Reflecting on everything covered in this learning path so far, which "
            "concepts do you feel least confident about, and what would help you "
            "understand them better?"
        )
        grounded_in = "twin_self_assessment" if personalization_summary else "none"

    return {
        "question_id": str(uuid.uuid4()),
        "category": "self_assessment_gaps",
        "question_text": question_text,
        "tests_skill": None,
        "module_title": None,
        "module_step": None,
        "source_files": [],
        "difficulty": "foundational",
        "grounded_in": grounded_in,
    }


def generate_assessment(
    project_id: str,
    developer_id: str,
    repo_metadata: Optional[dict] = None,
) -> dict:
    """
    Reuses generate_learning_path() as-is (already verified, untouched)
    to get ranked modules + Step 2 personalization tags + weak-skill
    summary in one call - no separate retrieval or Twin-lookup code.
    """
    learning_path_result = generate_learning_path(
        project_id,
        repo_metadata=repo_metadata,
        developer_id=developer_id,
    )

    modules = learning_path_result.get("learning_path", [])
    personalization_summary = learning_path_result.get("personalization_summary")

    questions = []
    used_steps: set = set()

    for category in CATEGORY_ORDER[:-1]:  # all except self_assessment_gaps
        module = _select_module_for_category(modules, category, used_steps)
        if module is not None:
            used_steps.add(module.get("step"))
        questions.append(_build_module_question(category, module))

    questions.append(_build_self_assessment_question(personalization_summary))

    return {
        "project_id": project_id,
        "developer_id": developer_id,
        "assessment_id": str(uuid.uuid4()),
        "questions": questions,
    }