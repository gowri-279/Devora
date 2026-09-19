"""
Deterministic formative quizzes for learning-path modules.

This module is intentionally separate from the final AI assessment.

Design goals:
- Questions are grounded in the module's actual course_content.
- No LLM/Bob dependency.
- Deterministic output for the same project/module/content.
- Correct answers are never exposed by the public quiz endpoint.
- Passing a quiz records module completion.
- Failing a quiz does not record progress.
- Developer progress is isolated by developer_id + project_id.
"""

import hashlib
import re
from datetime import datetime, timezone
from typing import Any

from app.db import get_module_progress_collection
from app.generate_learning_path import generate_learning_path

QUIZ_QUESTION_COUNT = 5


def _deterministic_index(seed: str, size: int) -> int:
    """Return a deterministic index based on a stable seed."""
    if size <= 0:
        return 0

    digest = hashlib.md5(seed.encode("utf-8")).hexdigest()
    return int(digest, 16) % size


def _get_learning_path(
    project_id: str,
    developer_id: str | None = None,
    repo_metadata: dict | None = None,
) -> list[dict]:
    """Generate and return the project's learning path."""
    result = generate_learning_path(
        project_id=project_id,
        repo_metadata=repo_metadata,
        developer_id=developer_id,
    )

    return result.get("learning_path", [])


def _find_module(
    learning_path: list[dict],
    module_step: int,
) -> dict | None:
    """Find a module by its numeric step."""
    for module in learning_path:
        if module.get("step") == module_step:
            return module

    return None


def _module_title(module: dict) -> str:
    return str(module.get("title") or f"Module {module.get('step', '')}").strip()


def _module_description(module: dict) -> str:
    return str(
        module.get("description")
        or module.get("purpose")
        or ""
    ).strip()


def _module_course_content(module: dict) -> list[dict]:
    """
    Normalize course_content into a list of dictionaries containing text.

    Supported shapes:
    - ["some text", "another text"]
    - [{"content": "..."}, {"text": "..."}]
    - [{"description": "..."}, {"topic": "..."}]
    """
    content = module.get("course_content", [])

    if isinstance(content, str):
        return [{"content": content}]

    if not isinstance(content, list):
        return []

    normalized = []

    for item in content:
        if isinstance(item, str):
            text = item.strip()
            if text:
                normalized.append({"content": text})
            continue

        if not isinstance(item, dict):
            continue

        text = ""

        for key in (
            "content",
            "text",
            "description",
            "topic",
            "title",
        ):
            value = item.get(key)

            if isinstance(value, str) and value.strip():
                text = value.strip()
                break

        if text:
            normalized.append(
                {
                    **item,
                    "content": text,
                }
            )

    return normalized


def _module_sources(module: dict) -> list[str]:
    """Return source files attached to a module."""
    sources = module.get("source_files")

    if sources is None:
        sources = module.get("sources", [])

    if isinstance(sources, str):
        return [sources]

    if isinstance(sources, list):
        return [
            str(source)
            for source in sources
            if source
        ]

    return []


def _clean_text(text: str) -> str:
    """Normalize whitespace while preserving readable content."""
    return re.sub(r"\s+", " ", text).strip()


def _extract_bullets(text: str) -> list[str]:
    """
    Extract Markdown bullet/numbered-list items.

    Examples:
    - Create feature branches
    - Open pull requests
    1. Install dependencies
    """
    bullets = []

    for line in text.splitlines():
        stripped = line.strip()

        match = re.match(
            r"^(?:[-*+]|\d+[.)])\s+(.+)$",
            stripped,
        )

        if not match:
            continue

        value = _clean_text(match.group(1))

        if len(value) >= 5:
            bullets.append(value)

    return bullets


def _extract_headings(text: str) -> list[str]:
    """Extract Markdown headings."""
    headings = []

    for line in text.splitlines():
        stripped = line.strip()

        match = re.match(r"^#{1,6}\s+(.+)$", stripped)

        if not match:
            continue

        heading = _clean_text(match.group(1))

        if heading:
            headings.append(heading)

    return headings


def _extract_sections(text: str) -> list[tuple[str, list[str]]]:
    """
    Extract simple Markdown sections.

    Returns:
        [(section_heading, [bullet1, bullet2, ...]), ...]
    """
    sections = []
    current_heading = None
    current_bullets = []

    for line in text.splitlines():
        stripped = line.strip()

        heading_match = re.match(
            r"^#{1,6}\s+(.+)$",
            stripped,
        )

        if heading_match:
            if current_heading and current_bullets:
                sections.append(
                    (
                        current_heading,
                        current_bullets,
                    )
                )

            current_heading = _clean_text(
                heading_match.group(1)
            )
            current_bullets = []
            continue

        bullet_match = re.match(
            r"^(?:[-*+]|\d+[.)])\s+(.+)$",
            stripped,
        )

        if bullet_match and current_heading:
            value = _clean_text(
                bullet_match.group(1)
            )

            if len(value) >= 5:
                current_bullets.append(value)

    if current_heading and current_bullets:
        sections.append(
            (
                current_heading,
                current_bullets,
            )
        )

    return sections


def _unique(items: list[str]) -> list[str]:
    """Return unique non-empty strings while preserving order."""
    seen = set()
    result = []

    for item in items:
        normalized = item.strip().lower()

        if not normalized or normalized in seen:
            continue

        seen.add(normalized)
        result.append(item.strip())

    return result


def _make_bullet_question(
    module: dict,
    bullet: str,
    all_bullets: list[str],
    question_number: int,
) -> dict:
    """
    Create a question testing recognition of a real practice/fact.

    Distractors are drawn from other real module bullets rather than
    generic filler whenever possible.
    """
    title = _module_title(module)

    distractor_candidates = [
        item
        for item in all_bullets
        if item.strip().lower() != bullet.strip().lower()
    ]

    seed = (
        f"{title}|{bullet}|{question_number}|"
        f"module-quiz-v2"
    )

    distractors = []

    if distractor_candidates:
        start = _deterministic_index(
            seed,
            len(distractor_candidates),
        )

        for offset in range(len(distractor_candidates)):
            candidate = distractor_candidates[
                (start + offset) % len(distractor_candidates)
            ]

            if candidate.lower() != bullet.lower():
                distractors.append(candidate)

            if len(distractors) == 3:
                break

    generic_distractors = [
        "A requirement that is not mentioned in this module.",
        "A task unrelated to the module's engineering practices.",
        "A deployment activity not covered by this material.",
    ]

    for candidate in generic_distractors:
        if len(distractors) >= 3:
            break

        if candidate not in distractors:
            distractors.append(candidate)

    options = [bullet] + distractors[:3]

    rotation = _deterministic_index(
        seed + "|rotation",
        len(options),
    )

    rotated_options = (
        options[rotation:]
        + options[:rotation]
    )

    correct_index = rotated_options.index(bullet)

    return {
        "question": (
            f"According to the '{title}' module, which of the "
            "following is explicitly included in the module's "
            "learning material?"
        ),
        "options": rotated_options,
        "hint": (
            f"Review the relevant practices and facts in the "
            f"'{title}' module."
        ),
        "module_step": module.get("step"),
        "module_title": title,
        "source_files": _module_sources(module),
        "_correct_index": correct_index,
        "_source_fact": bullet,
    }


def _make_section_question(
    module: dict,
    section_heading: str,
    section_bullets: list[str],
    all_sections: list[tuple[str, list[str]]],
    question_number: int,
) -> dict:
    """
    Ask which practice belongs to a particular section.

    Example:
        "Which practice belongs to the Git Workflow section?"
    """
    title = _module_title(module)

    correct_bullet = section_bullets[
        _deterministic_index(
            f"{title}|{section_heading}|{question_number}|section",
            len(section_bullets),
        )
    ]

    distractors = []

    for other_heading, other_bullets in all_sections:
        if other_heading.lower() == section_heading.lower():
            continue

        for bullet in other_bullets:
            if bullet.lower() == correct_bullet.lower():
                continue

            distractors.append(bullet)

    distractors = _unique(distractors)

    seed = (
        f"{title}|{section_heading}|{correct_bullet}|"
        f"{question_number}|module-quiz-section-v2"
    )

    if distractors:
        start = _deterministic_index(
            seed,
            len(distractors),
        )

        selected = []

        for offset in range(len(distractors)):
            candidate = distractors[
                (start + offset) % len(distractors)
            ]

            selected.append(candidate)

            if len(selected) == 3:
                break

        distractors = selected

    generic_distractors = [
        "A concept not mentioned in the module.",
        "An unrelated project-management activity.",
        "A deployment-only configuration step.",
    ]

    for candidate in generic_distractors:
        if len(distractors) >= 3:
            break

        if candidate not in distractors:
            distractors.append(candidate)

    options = [correct_bullet] + distractors[:3]

    rotation = _deterministic_index(
        seed + "|rotation",
        len(options),
    )

    rotated_options = (
        options[rotation:]
        + options[:rotation]
    )

    correct_index = rotated_options.index(correct_bullet)

    return {
        "question": (
            f"Which of the following belongs to the "
            f"'{section_heading}' section of the "
            f"'{title}' module?"
        ),
        "options": rotated_options,
        "hint": (
            f"Review the '{section_heading}' section of the "
            f"module material."
        ),
        "module_step": module.get("step"),
        "module_title": title,
        "source_files": _module_sources(module),
        "_correct_index": correct_index,
        "_source_fact": correct_bullet,
    }


def _make_heading_question(
    module: dict,
    heading: str,
    all_headings: list[str],
    question_number: int,
) -> dict:
    """
    Ask about an actual section/topic present in the module.
    """
    title = _module_title(module)

    distractors = [
        item
        for item in all_headings
        if item.lower() != heading.lower()
    ]

    generic_distractors = [
        "Unrelated Administration",
        "External Deployment",
        "Unspecified Project Task",
    ]

    for candidate in generic_distractors:
        if len(distractors) >= 3:
            break

        if candidate.lower() != heading.lower():
            distractors.append(candidate)

    seed = (
        f"{title}|heading|{heading}|{question_number}|"
        f"module-quiz-heading-v2"
    )

    start = _deterministic_index(
        seed,
        len(distractors) if distractors else 1,
    )

    selected = []

    if distractors:
        for offset in range(len(distractors)):
            candidate = distractors[
                (start + offset) % len(distractors)
            ]

            if candidate.lower() != heading.lower():
                selected.append(candidate)

            if len(selected) == 3:
                break

    options = [heading] + selected

    while len(options) < 4:
        fallback = generic_distractors[
            len(options) - 1
        ]

        if fallback not in options:
            options.append(fallback)

    rotation = _deterministic_index(
        seed + "|rotation",
        len(options),
    )

    rotated_options = (
        options[rotation:]
        + options[:rotation]
    )

    correct_index = rotated_options.index(heading)

    return {
        "question": (
            f"Which topic is explicitly covered in the "
            f"'{title}' module?"
        ),
        "options": rotated_options,
        "hint": (
            f"Review the section headings in the "
            f"'{title}' module."
        ),
        "module_step": module.get("step"),
        "module_title": title,
        "source_files": _module_sources(module),
        "_correct_index": correct_index,
        "_source_fact": heading,
    }


def _make_description_question(
    module: dict,
    question_number: int,
) -> dict:
    """
    Create a purpose question using the module's real description.

    This is kept as a fallback rather than the primary question type.
    """
    title = _module_title(module)
    description = _module_description(module)

    generic_options = [
        "Managing unrelated project administration tasks.",
        "Replacing all project documentation with generated code.",
        "Performing deployment without understanding the project.",
    ]

    seed = (
        f"{title}|description|{question_number}|"
        f"module-quiz-description-v2"
    )

    rotation = _deterministic_index(
        seed,
        len(generic_options) + 1,
    )

    options = [description] + generic_options

    rotated_options = (
        options[rotation:]
        + options[:rotation]
    )

    correct_index = rotated_options.index(description)

    return {
        "question": (
            f"Which statement best describes the purpose of "
            f"the '{title}' module?"
        ),
        "options": rotated_options,
        "hint": "Use the module's description as your guide.",
        "module_step": module.get("step"),
        "module_title": title,
        "source_files": _module_sources(module),
        "_correct_index": correct_index,
        "_source_fact": description,
    }


def _build_questions(module: dict) -> list[dict]:
    """
    Build deterministic questions grounded in actual module content.

    Preference order:
    1. Section-specific questions from real bullets.
    2. Questions about real module facts.
    3. Questions about real section headings.
    4. Description question as a final fallback.
    """
    questions = []

    content_items = _module_course_content(module)

    all_bullets = []
    all_headings = []
    all_sections = []

    for item in content_items:
        text = item.get("content", "")

        if not isinstance(text, str):
            continue

        all_bullets.extend(
            _extract_bullets(text)
        )

        all_headings.extend(
            _extract_headings(text)
        )

        all_sections.extend(
            _extract_sections(text)
        )

    all_bullets = _unique(all_bullets)
    all_headings = _unique(all_headings)

    # Prefer section-specific questions because they test
    # whether the learner understands where a concept belongs.
    usable_sections = [
        (heading, _unique(bullets))
        for heading, bullets in all_sections
        if bullets
    ]

    for question_number, (
        section_heading,
        section_bullets,
    ) in enumerate(
        usable_sections[:QUIZ_QUESTION_COUNT],
        start=1,
    ):
        questions.append(
            _make_section_question(
                module=module,
                section_heading=section_heading,
                section_bullets=section_bullets,
                all_sections=usable_sections,
                question_number=question_number,
            )
        )

    # If there were not enough usable sections, use actual bullets.
    for question_number, bullet in enumerate(
        all_bullets,
        start=len(questions) + 1,
    ):
        if len(questions) >= QUIZ_QUESTION_COUNT:
            break

        questions.append(
            _make_bullet_question(
                module=module,
                bullet=bullet,
                all_bullets=all_bullets,
                question_number=question_number,
            )
        )

    # Then fall back to actual headings.
    for question_number, heading in enumerate(
        all_headings,
        start=len(questions) + 1,
    ):
        if len(questions) >= QUIZ_QUESTION_COUNT:
            break

        questions.append(
            _make_heading_question(
                module=module,
                heading=heading,
                all_headings=all_headings,
                question_number=question_number,
            )
        )

    # Final fallback for modules with little/no structured content.
    if len(questions) < QUIZ_QUESTION_COUNT:
        questions.append(
            _make_description_question(
                module,
                question_number=len(questions) + 1,
            )
        )

    return questions[:QUIZ_QUESTION_COUNT]


def _public_question(question: dict) -> dict:
    """Remove private answer metadata before returning a quiz."""
    return {
        key: value
        for key, value in question.items()
        if not key.startswith("_")
    }


def generate_module_quiz(
    project_id: str,
    module_step: int,
    developer_id: str | None = None,
    repo_metadata: dict | None = None,
) -> dict:
    """
    Generate a deterministic quiz for one learning-path module.
    """
    learning_path = _get_learning_path(
        project_id=project_id,
        developer_id=developer_id,
        repo_metadata=repo_metadata,
    )

    module = _find_module(
        learning_path,
        module_step,
    )

    if not module:
        raise ValueError(
            f"Module step {module_step} was not found "
            f"for project '{project_id}'."
        )

    questions = _build_questions(module)

    return {
        "project_id": project_id,
        "module_step": module_step,
        "module_title": _module_title(module),
        "questions": [
            _public_question(question)
            for question in questions
        ],
    }


def _next_module_step(
    learning_path: list[dict],
    module_step: int,
) -> int | None:
    """Return the next higher module step, if one exists."""
    steps = sorted(
        module.get("step")
        for module in learning_path
        if isinstance(module.get("step"), int)
        and module.get("step") > module_step
    )

    return steps[0] if steps else None


def check_module_quiz(
    project_id: str,
    module_step: int,
    developer_id: str,
    answers: list[int],
    repo_metadata: dict | None = None,
) -> dict:
    """
    Check submitted answers.

    A module is completed only when every answer is correct.
    """
    if not developer_id:
        raise ValueError(
            "developer_id is required when checking a module quiz."
        )

    learning_path = _get_learning_path(
        project_id=project_id,
        developer_id=developer_id,
        repo_metadata=repo_metadata,
    )

    module = _find_module(
        learning_path,
        module_step,
    )

    if not module:
        raise ValueError(
            f"Module step {module_step} was not found "
            f"for project '{project_id}'."
        )

    questions = _build_questions(module)

    if len(answers) != len(questions):
        raise ValueError(
            f"Expected {len(questions)} answers, "
            f"received {len(answers)}."
        )

    correct_count = 0

    for question, answer in zip(questions, answers):
        try:
            answer_index = int(answer)
        except (TypeError, ValueError):
            answer_index = -1

        if answer_index == question.get("_correct_index"):
            correct_count += 1

    passed = (
        correct_count == len(questions)
        and len(questions) > 0
    )

    result = {
        "project_id": project_id,
        "developer_id": developer_id,
        "module_step": module_step,
        "module_title": _module_title(module),
        "score": correct_count,
        "total": len(questions),
        "passed": passed,
    }

    if not passed:
        result["message"] = (
            "Module quiz not passed. Review the module material "
            "and try again."
        )
        result["unlocked_next_step"] = None
        return result

    now = datetime.now(timezone.utc)

    collection = get_module_progress_collection()

    collection.update_one(
        {
            "developer_id": developer_id,
            "project_id": project_id,
            "module_step": module_step,
        },
        {
            "$set": {
                "developer_id": developer_id,
                "project_id": project_id,
                "module_step": module_step,
                "module_title": _module_title(module),
                "status": "completed",
                "completed_at": now,
                "updated_at": now,
            }
        },
        upsert=True,
    )

    next_step = _next_module_step(
        learning_path,
        module_step,
    )

    result["message"] = "Module quiz passed."
    result["unlocked_next_step"] = next_step

    return result


def get_module_progress(
    developer_id: str,
    project_id: str,
) -> list[dict[str, Any]]:
    """Return completed module progress for one developer/project."""
    documents = get_module_progress_collection().find(
        {
            "developer_id": developer_id,
            "project_id": project_id,
        },
        {
            "_id": 0,
        },
    ).sort("module_step", 1)

    return list(documents)

def complete_module_progress(
    developer_id: str,
    project_id: str,
    module_step: int,
):
    collection = get_module_progress_collection()

    now = datetime.now(timezone.utc)

    collection.update_one(
        {
            "developer_id": developer_id,
            "project_id": project_id,
            "module_step": module_step,
        },
        {
            "$set": {
                "developer_id": developer_id,
                "project_id": project_id,
                "module_step": module_step,
                "status": "completed",
                "completed_at": now,
                "updated_at": now,
            }
        },
        upsert=True,
    )

    return {
        "status": "success",
        "developer_id": developer_id,
        "project_id": project_id,
        "module_step": module_step,
    }