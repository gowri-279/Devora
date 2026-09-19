import json
import re

from app.models.schemas import (
    GenerateCurriculumRequest,
    GenerateCurriculumResponse,
)
from app.services.ibm_bob_client import IBMBobClient


def generate_curriculum(
    request: GenerateCurriculumRequest,
) -> GenerateCurriculumResponse:

    prompt = build_curriculum_prompt(request)

    client = IBMBobClient()
    raw_response = client.generate(prompt)

    data = _parse_json_response(raw_response)

    if not isinstance(data, dict):
        raise RuntimeError(
            "IBM Bob returned an invalid curriculum response."
        )

    modules = data.get("modules")

    if not isinstance(modules, list) or not modules:
        raise RuntimeError(
            "IBM Bob returned no curriculum modules."
        )

    normalized_modules = []

    for module in modules:
        if not isinstance(module, dict):
            continue

        lessons = module.get("lessons", [])

        if not isinstance(lessons, list):
            lessons = []

        normalized_lessons = []

        for lesson in lessons:
            if not isinstance(lesson, dict):
                continue

            sources = lesson.get("sources", [])

            if not isinstance(sources, list):
                sources = []

            normalized_sources = []

            for source in sources:
                if not isinstance(source, dict):
                    continue

                normalized_sources.append({
                    "source_file": str(
                        source.get("source_file", "")
                    ),
                    "section_title": str(
                        source.get("section_title", "")
                    ),
                    "evidence": str(
                        source.get("evidence", "")
                    ),
                })

            repository_exploration = lesson.get(
                "repository_exploration",
                [],
            )

            if not isinstance(repository_exploration, list):
                repository_exploration = []

            normalized_lessons.append({
                "concept": str(
                    lesson.get("concept", "")
                ),
                "explanation": str(
                    lesson.get("explanation", "")
                ),
                "why_it_matters": str(
                    lesson.get("why_it_matters", "")
                ),
                "how_project_implements_it": str(
                    lesson.get(
                        "how_project_implements_it",
                        "",
                    )
                ),
                "repository_exploration": [
                    str(item)
                    for item in repository_exploration
                    if item
                ],
                "key_takeaway": str(
                    lesson.get("key_takeaway", "")
                ),
                "sources": normalized_sources,
            })

        try:
            estimated_minutes = int(
                module.get("estimated_minutes", 20)
            )
        except (TypeError, ValueError):
            estimated_minutes = 20

        learning_objectives = module.get(
            "learning_objectives",
            [],
        )

        if not isinstance(learning_objectives, list):
            learning_objectives = []

        prerequisites = module.get(
            "prerequisites",
            [],
        )

        if not isinstance(prerequisites, list):
            prerequisites = []

        normalized_modules.append({
            "title": str(
                module.get(
                    "title",
                    "Project Concept",
                )
            ),
            "description": str(
                module.get("description", "")
            ),
            "difficulty": str(
                module.get("difficulty", "medium")
            ),
            "estimated_minutes": estimated_minutes,
            "learning_objectives": [
                str(item)
                for item in learning_objectives
                if item
            ],
            "prerequisites": [
                str(item)
                for item in prerequisites
                if item
            ],
            "lessons": normalized_lessons,
        })

    if not normalized_modules:
        raise RuntimeError(
            "No usable curriculum modules were generated."
        )

    return GenerateCurriculumResponse(
        project_id=request.project_id,
        modules=normalized_modules,
    )


def build_curriculum_prompt(
    request: GenerateCurriculumRequest,
) -> str:

    repository_modules = json.dumps(
        request.repository_modules,
        indent=2,
    )

    repository_summary = json.dumps(
        request.repository_summary,
        indent=2,
    )

    project_evidence = json.dumps(
        request.project_evidence,
        indent=2,
    )

    developer_profile = json.dumps(
        request.developer_profile or {},
        indent=2,
    )

    return f"""
You are DEVORA, an intelligent software-project onboarding
curriculum generator.

Your task is to create a REAL developer onboarding curriculum
for the supplied software project.

Do NOT simply turn repository files into learning modules.

Instead:

1. Understand the repository structure.
2. Identify the important technical concepts in the project.
3. Identify relationships between those concepts.
4. Identify prerequisites.
5. Group related concepts into coherent learning modules.
6. Order modules from foundational knowledge to advanced knowledge.
7. Decide dynamically how many modules are appropriate.
8. Generate teaching material grounded ONLY in the supplied evidence.
9. Tell the developer exactly where to explore the repository.
10. Attach exact source references to every lesson.

The curriculum must be specific to THIS project.

Do NOT use a generic tutorial structure unless the repository
evidence supports it.

Do NOT invent frameworks, architecture, files, classes,
functions, authentication mechanisms, APIs, or workflows.

If something cannot be established from the evidence, say so
rather than inventing it.

The output MUST be valid JSON.

Return exactly this structure:

{{
  "modules": [
    {{
      "title": "Module title",
      "description": "What the developer will learn",
      "difficulty": "easy|medium|hard",
      "estimated_minutes": 20,
      "learning_objectives": [
        "objective 1",
        "objective 2"
      ],
      "prerequisites": [
        "previous concept"
      ],
      "lessons": [
        {{
          "concept": "Concept being taught",
          "explanation": "Clear explanation of the concept",
          "why_it_matters": "Why this matters in this project",
          "how_project_implements_it":
            "How the supplied project implements it",
          "repository_exploration": [
            "Inspect path/to/file.py and trace X"
          ],
          "key_takeaway": "The key thing the developer should remember",
          "sources": [
            {{
              "source_file": "path/to/file.py",
              "section_title": "Relevant section",
              "evidence": "Short evidence from supplied context"
            }}
          ]
        }}
      ]
    }}
  ]
}}

IMPORTANT:
- Modules must be dynamically selected based on the project's actual
  architecture, concepts, dependencies, workflows, and evidence.
- For a project of meaningful complexity, generate enough modules to
  cover the major architectural and implementation concepts.
- Do not collapse substantially different concepts into one module
  merely to keep the curriculum short.
- Do not force a fixed number of modules, but typically generate
  around 6-10 modules when the repository contains enough distinct
  concepts to justify them.
- Do not create one module per file.
- Do not dump source code into explanations.
- Do not reproduce entire files.
- Use concise explanations.
- Source references must correspond to supplied evidence.
- Prefer important architectural concepts over trivial files.
- Include repository exploration instructions where useful.
- A module can contain multiple related lessons.
- A lesson can reference multiple source files.
- Start with concepts a new developer must understand before
  moving into deeper implementation details.

PROJECT ID:
{request.project_id}

REPOSITORY SUMMARY:
{repository_summary}

REPOSITORY INTELLIGENCE:
{repository_modules}

PROJECT / DOCUMENTATION EVIDENCE:
{project_evidence}

DEVELOPER PROFILE:
{developer_profile}
""".strip()


def _parse_json_response(response: str) -> dict:
    """
    Robustly extract a JSON object from IBM Bob's response.

    Bob may return:
    - plain JSON
    - JSON inside ```json fences
    - JSON inside generic ``` fences
    - explanatory text before/after the JSON
    - multiple JSON objects/events
    - a JSON object followed by trailing text

    The parser always prefers an object containing a
    non-empty `modules` list.
    """

    if not isinstance(response, str):
        raise RuntimeError(
            "IBM Bob returned a non-text curriculum response."
        )

    response = response.strip()

    if not response:
        raise RuntimeError(
            "IBM Bob returned an empty curriculum response."
        )

    # ---------------------------------------------------------
    # 1. Direct JSON
    # ---------------------------------------------------------
    try:
        parsed = json.loads(response)

        if isinstance(parsed, dict):
            return parsed

    except json.JSONDecodeError:
        pass

    # ---------------------------------------------------------
    # 2. JSON inside Markdown code fences
    # ---------------------------------------------------------
    fenced_blocks = re.findall(
        r"```(?:json|JSON)?\s*(.*?)\s*```",
        response,
        re.DOTALL,
    )

    for block in fenced_blocks:
        block = block.strip()

        try:
            parsed = json.loads(block)

            if isinstance(parsed, dict):
                return parsed

        except json.JSONDecodeError:
            continue

    # ---------------------------------------------------------
    # 3. Extract JSON objects using JSONDecoder.raw_decode
    #
    # This is more reliable than response.find("{") and
    # response.rfind("}") because it correctly handles:
    #
    #   explanatory text
    #   { valid JSON }
    #   trailing text
    #
    # and nested braces inside the JSON itself.
    # ---------------------------------------------------------
    decoder = json.JSONDecoder()

    for match in re.finditer(r"\{", response):
        start = match.start()

        try:
            parsed, _ = decoder.raw_decode(
                response[start:]
            )

        except json.JSONDecodeError:
            continue

        if isinstance(parsed, dict):
            modules = parsed.get("modules")

            if isinstance(modules, list) and modules:
                return parsed

    # ---------------------------------------------------------
    # 4. Fallback: scan all possible JSON objects and prefer
    #    the one that actually contains curriculum modules.
    # ---------------------------------------------------------
    candidates = []

    for match in re.finditer(r"\{", response):
        start = match.start()

        try:
            parsed, _ = decoder.raw_decode(
                response[start:]
            )

        except json.JSONDecodeError:
            continue

        if isinstance(parsed, dict):
            candidates.append(parsed)

    for candidate in candidates:
        modules = candidate.get("modules")

        if isinstance(modules, list) and modules:
            return candidate

    # ---------------------------------------------------------
    # 5. Nothing usable was found.
    #
    # Include only a bounded preview so an enormous Bob
    # response does not flood the server logs.
    # ---------------------------------------------------------
    preview = response[:1200]

    raise RuntimeError(
        "IBM Bob returned curriculum text that could not "
        "be parsed as JSON. "
        f"Response preview: {preview}"
    )
