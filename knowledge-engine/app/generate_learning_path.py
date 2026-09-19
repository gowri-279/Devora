from pathlib import Path
from typing import Optional

from pydantic import BaseModel

from app.raw_storage import (
    list_raw_documents,
    list_raw_document_content,
)

from app.repository_intelligence import (
    build_repository_modules,
    repository_summary,
)

from app.developer_twin import get_twin
from app.learning_path_personalization import personalize_modules
from app.curriculum_client import generate_curriculum


class LearningPathRequest(BaseModel):
    project_id: str
    repo_metadata: Optional[dict] = None
    developer_id: Optional[str] = None


# ==========================================================
# PATH HELPERS
# ==========================================================


def _normalize_path(path: str) -> str:
    """
    Normalize repository/document paths so comparisons work
    across Windows/macOS/Linux path separators.
    """

    return str(path or "").replace("\\", "/").strip("/")


def _source_name(source_file: str) -> str:
    """
    Return the filename portion of a repository path.
    """

    return Path(source_file).name


def _source_belongs_to_module(
    source_file: str,
    module_path: str,
) -> bool:
    """
    Determine whether a stored raw document belongs to a
    curriculum source selected by repository intelligence / AI.

    Repository metadata may contain:
        /tmp/.../source/app/main.py

    while raw storage may contain:
        app/main.py

    or vice versa.

    This helper therefore supports:
        1. exact normalized matches
        2. repository-relative suffix matches
        3. module-directory matches
    """

    source = _normalize_path(source_file)
    module = _normalize_path(module_path)

    if not source or not module:
        return False

    # ------------------------------------------------------
    # Exact match
    # ------------------------------------------------------

    if source == module:
        return True

    # ------------------------------------------------------
    # Remove temporary repository extraction prefixes.
    #
    # Parser/ingestion paths may look like:
    #
    # /var/folders/.../source/app/main.py
    #
    # while curriculum source references may be:
    #
    # app/main.py
    # ------------------------------------------------------

    source_marker = "/source/"
    module_marker = "/source/"

    if source_marker in source:
        source = source.split(
            source_marker,
            1,
        )[1]

    if module_marker in module:
        module = module.split(
            module_marker,
            1,
        )[1]

    # ------------------------------------------------------
    # Exact repository-relative match
    # ------------------------------------------------------

    if source == module:
        return True

    # ------------------------------------------------------
    # Suffix match.
    #
    # Example:
    #
    # source:
    #   /tmp/repo/app/main.py
    #
    # module:
    #   app/main.py
    # ------------------------------------------------------

    if source.endswith("/" + module):
        return True

    if module.endswith("/" + source):
        return True

    # ------------------------------------------------------
    # Directory match.
    #
    # This supports a module path such as:
    #
    # app
    #
    # matching:
    #
    # app/main.py
    # app/config.py
    # ------------------------------------------------------

    source_path = Path(source)
    module_path_obj = Path(module)

    if source_path.parent == module_path_obj:
        return True

    # If module itself is a directory, check whether the
    # source file is directly underneath that directory.
    if module.endswith("/"):
        return source.startswith(module)

    return False


# ==========================================================
# COURSE CONTENT ATTACHMENT
# ==========================================================


def _attach_course_content(
    modules: list,
    raw_documents: list,
    max_chars_per_module: int = 18000,
    max_chars_per_source: int = 6000,
) -> list:
    """
    Attach real stored source/document content to each
    curriculum module.

    The AI generates:
        sources / source_files

    Raw storage contains:
        source_file + complete original text

    This function connects the two layers.

    Only the source files actually referenced by the
    curriculum are attached.

    Content is bounded so one module cannot return an
    excessively large response.
    """

    if not modules or not raw_documents:
        return modules

    # ------------------------------------------------------
    # Index raw documents.
    #
    # Keep the first occurrence of each normalized source.
    # ------------------------------------------------------

    documents = []

    for document in raw_documents:

        if not isinstance(document, dict):
            continue

        source_file = _normalize_path(
            document.get(
                "source_file",
                "",
            )
        )

        if not source_file:
            continue

        text = str(
            document.get(
                "text",
                "",
            )
            or ""
        )

        if not text.strip():
            continue

        documents.append(
            {
                **document,
                "source_file": source_file,
                "text": text,
            }
        )

    # ------------------------------------------------------
    # Attach content module by module.
    # ------------------------------------------------------

    for module in modules:

        if not isinstance(module, dict):
            continue

        source_files = module.get(
            "source_files",
            [],
        )

        if not isinstance(source_files, list):
            source_files = []

        # Also inspect lesson-level sources in case the
        # module-level source list is missing.
        if not source_files:

            for lesson in module.get(
                "lessons",
                [],
            ):

                if not isinstance(
                    lesson,
                    dict,
                ):
                    continue

                for source in lesson.get(
                    "sources",
                    [],
                ):

                    if isinstance(
                        source,
                        dict,
                    ):
                        source_file = source.get(
                            "source_file",
                            "",
                        )
                    else:
                        source_file = str(
                            source
                        )

                    source_file = _normalize_path(
                        source_file
                    )

                    if (
                        source_file
                        and source_file
                        not in source_files
                    ):
                        source_files.append(
                            source_file
                        )

        course_content = []
        module_chars = 0

        # --------------------------------------------------
        # Match each curriculum source against raw storage.
        # --------------------------------------------------

        for requested_source in source_files:

            requested_source = _normalize_path(
                requested_source
            )

            if not requested_source:
                continue

            matched_document = None

            for document in documents:

                if _source_belongs_to_module(
                    document.get(
                        "source_file",
                        "",
                    ),
                    requested_source,
                ):
                    matched_document = document
                    break

            if not matched_document:
                continue

            content = str(
                matched_document.get(
                    "text",
                    "",
                )
                or ""
            ).strip()

            if not content:
                continue

            remaining = (
                max_chars_per_module
                - module_chars
            )

            if remaining <= 0:
                break

            content = content[
                :min(
                    max_chars_per_source,
                    remaining,
                )
            ]

            actual_source_file = _normalize_path(
                matched_document.get(
                    "source_file",
                    requested_source,
                )
            )

            filename = _source_name(
                actual_source_file
            )

            course_content.append(
                {
                    "source_file":
                        actual_source_file,

                    "filename":
                        filename,

                    "scope":
                        matched_document.get(
                            "scope",
                            "project",
                        ),

                    "content":
                        content,
                }
            )

            module_chars += len(content)

        module["course_content"] = (
            course_content
        )

    return modules


# ==========================================================
# REPOSITORY FILTER HELPERS
# ==========================================================


def _is_repository_noise(source_file: str) -> bool:
    """
    Identify repository-management material that should not
    dominate curriculum generation.

    These files can still remain in the Knowledge Engine and
    knowledge base. They are simply low-priority for onboarding
    curriculum generation.
    """

    path = _normalize_path(source_file).lower()

    if not path:
        return True

    noise_prefixes = (
        ".git/",
        ".github/",
        ".gitlab/",
        ".circleci/",
        ".azure/",
        ".buildkite/",
        "ci/",
        "cd/",
    )

    if path.startswith(noise_prefixes):
        return True

    noise_fragments = (
        "/issue_template",
        "/issue-templates/",
        "/pull_request_template",
        "/dependabot",
        "/release/",
        "/releases/",
        "/translations/",
        "/translation/",
    )

    if any(
        fragment in path
        for fragment in noise_fragments
    ):
        return True

    filename = _source_name(path)

    noise_filenames = {
        "dependabot.yml",
        "dependabot.yaml",
    }

    if filename in noise_filenames:
        return True

    return False


def _is_documentation(source_file: str) -> bool:
    """
    Identify documentation-oriented sources.
    """

    path = _normalize_path(source_file).lower()
    name = _source_name(path)

    if name in {
        "readme",
        "readme.md",
        "readme.rst",
        "readme.txt",
    }:
        return True

    if path.startswith("docs/"):
        return True

    if "/docs/" in path:
        return True

    if name.endswith(
        (
            ".md",
            ".rst",
            ".txt",
        )
    ):
        return True

    return False


def _is_configuration(source_file: str) -> bool:
    """
    Identify configuration/dependency files that can help
    explain project architecture without overwhelming the model.
    """

    path = _normalize_path(source_file).lower()
    name = _source_name(path)

    configuration_names = {
        "pyproject.toml",
        "requirements.txt",
        "requirements-dev.txt",
        "package.json",
        "package-lock.json",
        "pnpm-lock.yaml",
        "yarn.lock",
        "cargo.toml",
        "go.mod",
        "pom.xml",
        "build.gradle",
        "build.gradle.kts",
        "dockerfile",
        "docker-compose.yml",
        "docker-compose.yaml",
        ".env.example",
    }

    if name in configuration_names:
        return True

    return False


def _is_source_code(source_file: str) -> bool:
    """
    Identify common source-code files.

    This is intentionally language-agnostic and is NOT tied
    to FastAPI or any particular framework.
    """

    path = _normalize_path(source_file).lower()

    source_extensions = (
        ".py",
        ".js",
        ".jsx",
        ".ts",
        ".tsx",
        ".java",
        ".go",
        ".rs",
        ".cpp",
        ".cc",
        ".c",
        ".h",
        ".hpp",
        ".cs",
        ".kt",
        ".kts",
        ".swift",
        ".rb",
        ".php",
        ".scala",
        ".sql",
    )

    return path.endswith(
        source_extensions
    )


def _evidence_priority(
    source_file: str,
    preferred_sources: list,
) -> int:
    """
    Assign a curriculum-evidence priority.

    Lower number = higher priority.

    Priority:
        0 -> explicitly selected repository-intelligence source
        1 -> application source code
        2 -> README / docs
        3 -> important configuration
        4 -> project/team documentation
        5 -> everything else
        99 -> repository-management noise
    """

    normalized = _normalize_path(
        source_file
    )

    if not normalized:
        return 99

    if _is_repository_noise(
        normalized
    ):
        return 99

    if normalized in preferred_sources:
        return 0

    if _is_source_code(
        normalized
    ):
        return 1

    if _is_documentation(
        normalized
    ):
        return 2

    if _is_configuration(
        normalized
    ):
        return 3

    return 5


# ==========================================================
# PROJECT EVIDENCE
# ==========================================================


def _build_project_evidence(
    raw_documents: list,
    repo_modules: list,
    repo_metadata: Optional[dict] = None,
    max_chars: int = 12000,
    max_records: int = 12,
    max_chars_per_record: int = 1600,
) -> list:
    """
    Build compact, grounded evidence for curriculum generation.

    The complete original documents remain stored in MongoDB.

    This function only sends small evidence snippets to the AI
    curriculum generator.
    """

    evidence = []
    total_chars = 0

    # ------------------------------------------------------
    # Collect preferred source paths from repository intelligence
    # ------------------------------------------------------

    preferred_sources = []

    for module in repo_modules:

        if not isinstance(module, dict):
            continue

        for source in module.get(
            "source_files",
            [],
        ):

            normalized = _normalize_path(
                source
            )

            if (
                normalized
                and not _is_repository_noise(
                    normalized
                )
                and normalized
                not in preferred_sources
            ):
                preferred_sources.append(
                    normalized
                )

        for source in module.get(
            "sources",
            [],
        ):

            normalized = _normalize_path(
                source
            )

            if (
                normalized
                and not _is_repository_noise(
                    normalized
                )
                and normalized
                not in preferred_sources
            ):
                preferred_sources.append(
                    normalized
                )

    # ------------------------------------------------------
    # Also inspect repository metadata for useful source paths
    # ------------------------------------------------------

    if isinstance(
        repo_metadata,
        dict,
    ):

        candidate_lists = (
            repo_metadata.get(
                "entrypoints",
                [],
            ),
            repo_metadata.get(
                "source_files",
                [],
            ),
            repo_metadata.get(
                "files",
                [],
            ),
        )

        for candidates in candidate_lists:

            if not isinstance(
                candidates,
                list,
            ):
                continue

            for source in candidates:

                if isinstance(
                    source,
                    dict,
                ):

                    source = (
                        source.get(
                            "path"
                        )
                        or source.get(
                            "file"
                        )
                        or source.get(
                            "source_file"
                        )
                        or ""
                    )

                normalized = _normalize_path(
                    source
                )

                if (
                    normalized
                    and not _is_repository_noise(
                        normalized
                    )
                    and normalized
                    not in preferred_sources
                ):
                    preferred_sources.append(
                        normalized
                    )

    # ------------------------------------------------------
    # Index raw documents
    # ------------------------------------------------------

    documents_by_source = {}

    for document in raw_documents:

        if not isinstance(
            document,
            dict,
        ):
            continue

        source_file = _normalize_path(
            document.get(
                "source_file",
                "",
            )
        )

        if not source_file:
            continue

        if source_file not in documents_by_source:
            documents_by_source[
                source_file
            ] = document

    # ------------------------------------------------------
    # Build candidate documents
    # ------------------------------------------------------

    candidates = []

    for (
        source_file,
        document,
    ) in documents_by_source.items():

        if _is_repository_noise(
            source_file
        ):
            continue

        priority = _evidence_priority(
            source_file,
            preferred_sources,
        )

        scope = document.get(
            "scope",
            "project",
        )

        if scope in {
            "team",
            "project",
        }:

            if priority > 3:
                priority = 4

        candidates.append(
            (
                priority,
                source_file,
                document,
            )
        )

    # ------------------------------------------------------
    # Stable deterministic ordering
    # ------------------------------------------------------

    candidates.sort(
        key=lambda item: (
            item[0],
            item[1].lower(),
        )
    )

    # ------------------------------------------------------
    # Build bounded evidence
    # ------------------------------------------------------

    for (
        priority,
        source_file,
        document,
    ) in candidates:

        if len(evidence) >= max_records:
            break

        if total_chars >= max_chars:
            break

        text = str(
            document.get(
                "text",
                "",
            )
            or ""
        )

        if not text.strip():
            continue

        remaining = (
            max_chars - total_chars
        )

        if remaining <= 0:
            break

        snippet_size = min(
            max_chars_per_record,
            remaining,
        )

        snippet = text[
            :snippet_size
        ].strip()

        if not snippet:
            continue

        evidence_role = (
            "repository_source"
        )

        if priority == 2:
            evidence_role = (
                "project_documentation"
            )

        elif priority == 3:
            evidence_role = (
                "project_configuration"
            )

        elif priority == 4:
            evidence_role = (
                "team_project_context"
            )

        evidence.append(
            {
                "source_file":
                    source_file,

                "section_title":
                    str(
                        document.get(
                            "section_title",
                            "",
                        )
                        or ""
                    ),

                "scope":
                    document.get(
                        "scope",
                        "project",
                    ),

                "evidence_role":
                    evidence_role,

                "evidence":
                    snippet,
            }
        )

        total_chars += len(
            snippet
        )

    return evidence


# ==========================================================
# CURRICULUM SOURCE EXTRACTION
# ==========================================================


def _extract_module_sources(
    module: dict,
) -> list:
    """
    Extract unique source files referenced by all lessons
    in an AI-generated curriculum module.
    """

    sources = []

    for lesson in module.get(
        "lessons",
        [],
    ):

        if not isinstance(
            lesson,
            dict,
        ):
            continue

        for source in lesson.get(
            "sources",
            [],
        ):

            if isinstance(
                source,
                dict,
            ):

                source_file = source.get(
                    "source_file",
                    "",
                )

            else:

                source_file = str(
                    source
                )

            source_file = _normalize_path(
                source_file
            )

            if (
                source_file
                and source_file
                not in sources
            ):
                sources.append(
                    source_file
                )

    # Compatibility with source_files.
    for source in module.get(
        "source_files",
        [],
    ):

        source_file = _normalize_path(
            source
        )

        if (
            source_file
            and source_file
            not in sources
        ):
            sources.append(
                source_file
            )

    # Compatibility with sources.
    for source in module.get(
        "sources",
        [],
    ):

        if isinstance(
            source,
            dict,
        ):

            source_file = source.get(
                "source_file",
                "",
            )

        else:

            source_file = str(
                source
            )

        source_file = _normalize_path(
            source_file
        )

        if (
            source_file
            and source_file
            not in sources
        ):
            sources.append(
                source_file
            )

    return sources


# ==========================================================
# CURRICULUM NORMALIZATION
# ==========================================================


def _normalize_curriculum_modules(
    project_id: str,
    modules: list,
    raw_documents: Optional[list] = None,
) -> list:
    """
    Normalize AI-generated curriculum modules while preserving
    the structured lesson format.

    Frontend-compatible fields are added.

    If raw_documents are available, actual stored source content
    is attached to the module's course_content field.
    """

    normalized_modules = []

    for index, module in enumerate(
        modules,
        start=1,
    ):

        if not isinstance(
            module,
            dict,
        ):
            continue

        # --------------------------------------------------
        # Basic module fields
        # --------------------------------------------------

        title = str(
            module.get(
                "title",
                f"Project Module {index}",
            )
            or f"Project Module {index}"
        ).strip()

        description = str(
            module.get(
                "description",
                "",
            )
            or ""
        ).strip()

        difficulty = str(
            module.get(
                "difficulty",
                "medium",
            )
            or "medium"
        ).strip().lower()

        if difficulty not in {
            "easy",
            "medium",
            "hard",
        }:
            difficulty = "medium"

        try:
            estimated_minutes = int(
                module.get(
                    "estimated_minutes",
                    20,
                )
            )
        except (
            TypeError,
            ValueError,
        ):
            estimated_minutes = 20

        estimated_minutes = max(
            5,
            estimated_minutes,
        )

        # --------------------------------------------------
        # Learning objectives
        # --------------------------------------------------

        learning_objectives = []

        raw_objectives = module.get(
            "learning_objectives",
            [],
        )

        if isinstance(
            raw_objectives,
            list,
        ):

            for objective in raw_objectives:

                if not objective:
                    continue

                objective_text = str(
                    objective
                ).strip()

                if (
                    objective_text
                    and objective_text
                    not in learning_objectives
                ):

                    learning_objectives.append(
                        objective_text
                    )

        # --------------------------------------------------
        # Prerequisites
        # --------------------------------------------------

        prerequisites = []

        raw_prerequisites = module.get(
            "prerequisites",
            [],
        )

        if isinstance(
            raw_prerequisites,
            list,
        ):

            for prerequisite in raw_prerequisites:

                if not prerequisite:
                    continue

                prerequisite_text = str(
                    prerequisite
                ).strip()

                if (
                    prerequisite_text
                    and prerequisite_text
                    not in prerequisites
                ):

                    prerequisites.append(
                        prerequisite_text
                    )

        # --------------------------------------------------
        # Lessons
        # --------------------------------------------------

        normalized_lessons = []

        raw_lessons = module.get(
            "lessons",
            [],
        )

        if not isinstance(
            raw_lessons,
            list,
        ):

            raw_lessons = []

        for (
            lesson_index,
            lesson,
        ) in enumerate(
            raw_lessons,
            start=1,
        ):

            if not isinstance(
                lesson,
                dict,
            ):
                continue

            concept = str(
                lesson.get(
                    "concept",
                    f"Lesson {lesson_index}",
                )
                or f"Lesson {lesson_index}"
            ).strip()

            explanation = str(
                lesson.get(
                    "explanation",
                    "",
                )
                or ""
            ).strip()

            why_it_matters = str(
                lesson.get(
                    "why_it_matters",
                    "",
                )
                or ""
            ).strip()

            how_project_implements_it = str(
                lesson.get(
                    "how_project_implements_it",
                    "",
                )
                or ""
            ).strip()

            key_takeaway = str(
                lesson.get(
                    "key_takeaway",
                    "",
                )
                or ""
            ).strip()

            # --------------------------------------------------
            # Repository exploration
            # --------------------------------------------------

            repository_exploration = []

            raw_exploration = lesson.get(
                "repository_exploration",
                [],
            )

            if isinstance(
                raw_exploration,
                list,
            ):

                for item in raw_exploration:

                    if not item:
                        continue

                    exploration_text = str(
                        item
                    ).strip()

                    if exploration_text:
                        repository_exploration.append(
                            exploration_text
                        )

            # --------------------------------------------------
            # Lesson source references
            # --------------------------------------------------

            lesson_sources = []

            raw_sources = lesson.get(
                "sources",
                [],
            )

            if isinstance(
                raw_sources,
                list,
            ):

                for source in raw_sources:

                    if isinstance(
                        source,
                        dict,
                    ):

                        source_file = _normalize_path(
                            source.get(
                                "source_file",
                                "",
                            )
                        )

                        section_title = str(
                            source.get(
                                "section_title",
                                "",
                            )
                            or ""
                        ).strip()

                        evidence = str(
                            source.get(
                                "evidence",
                                "",
                            )
                            or ""
                        ).strip()

                    else:

                        source_file = _normalize_path(
                            source
                        )

                        section_title = ""
                        evidence = ""

                    if not source_file:
                        continue

                    lesson_sources.append(
                        {
                            "source_file":
                                source_file,

                            "section_title":
                                section_title,

                            "evidence":
                                evidence,
                        }
                    )

            normalized_lessons.append(
                {
                    "step":
                        lesson_index,

                    "concept":
                        concept,

                    "explanation":
                        explanation,

                    "why_it_matters":
                        why_it_matters,

                    "how_project_implements_it":
                        how_project_implements_it,

                    "repository_exploration":
                        repository_exploration,

                    "key_takeaway":
                        key_takeaway,

                    "sources":
                        lesson_sources,
                }
            )

        # --------------------------------------------------
        # Module-level source list
        # --------------------------------------------------

        source_files = _extract_module_sources(
            {
                **module,
                "lessons": normalized_lessons,
            }
        )

        if not source_files:
           source_files = []

           # Fallback to actual stored repository documents.
        for document in raw_documents or []:
           if not isinstance(document, dict):
            continue
           source_file = _normalize_path(
                document.get("source_file", "")
            )
           if (
               source_file
               and source_file not in source_files
            ):
            source_files.append(source_file)
        print("SOURCE FALLBACK:", source_files)

        # --------------------------------------------------
        # Frontend-compatible module
        # --------------------------------------------------

        normalized_module = {
            "step":
                index,

            "title":
                title,

            "description":
                description,

            "purpose":
                description,

            "difficulty":
                difficulty,

            "estimated_minutes":
                estimated_minutes,

            "learning_objectives":
                learning_objectives,

            "prerequisites":
                prerequisites,

            "lessons":
                normalized_lessons,

            "sources":
                source_files,

            "source_files":
                source_files,

            # Real source content is attached below
            # after normalization.
            "course_content":
                [],

            "content_type":
                "ai_generated_grounded_curriculum",

            "project_id":
                project_id,
        }

        normalized_modules.append(
            normalized_module
        )

    # ------------------------------------------------------
    # Attach actual source content.
    # ------------------------------------------------------

    if raw_documents:
        _attach_course_content(
            modules=normalized_modules,
            raw_documents=raw_documents,
        )

    return normalized_modules


# ==========================================================
# DOCUMENTATION-ONLY CURRICULUM
# ==========================================================


def _generate_documentation_curriculum(
    project_id: str,
    raw_documents: list,
    developer_id: Optional[str] = None,
) -> dict:
    """
    Generate a dynamic curriculum when repository metadata
    is unavailable.

    Documentation is used as the grounding evidence.
    """

    project_evidence = _build_project_evidence(
        raw_documents=raw_documents,
        repo_modules=[],
        repo_metadata=None,
    )

    developer_profile = None

    if developer_id:

        developer_profile = get_twin(
            developer_id,
            project_id,
        )

    curriculum = generate_curriculum(
        project_id=project_id,
        repository_summary={},
        repository_modules=[],
        project_evidence=project_evidence,
        developer_profile=developer_profile,
    )

    modules = _normalize_curriculum_modules(
        project_id=project_id,
        modules=curriculum.get(
            "modules",
            [],
        ),
        raw_documents=raw_documents,
    )

    result = {
        "project_id":
            project_id,

        "learning_path":
            modules,

        "repository_summary":
            None,

        "mode":
            "documentation_only",
    }

    if developer_id:

        twin = get_twin(
            developer_id,
            project_id,
        )

        if twin:

            result["personalization_summary"] = (
                personalize_modules(
                    modules,
                    twin,
                )
            )

    return result


# ==========================================================
# MAIN LEARNING-PATH GENERATOR
# ==========================================================


def generate_learning_path(
    project_id: str,
    repo_metadata: Optional[dict] = None,
    developer_id: Optional[str] = None,
):
    """
    Generate a project-specific developer onboarding curriculum.

    Architecture:

        Repository Parser
                ↓
        repository metadata
                ↓
        Repository Intelligence
                ↓
        candidate architectural areas
                +
        bounded project/document evidence
                ↓
        AI Curriculum Generator
                ↓
        structured onboarding curriculum
                +
        actual stored source content
                ↓
        Developer Twin personalization

    Repository intelligence is evidence/candidate discovery,
    NOT the final curriculum.
    """

    print(
        "\n🔥 GENERATE_LEARNING_PATH FUNCTION WAS CALLED 🔥"
    )

    # ======================================================
    # DOCUMENT DISCOVERY
    # ======================================================

    docs = list_raw_documents(
        project_id=project_id
    )

    source_files = [
        d.get(
            "source_file",
            "",
        )
        for d in docs
        if d.get("source_file")
    ]

    print(
        "Document metadata available:",
        len(source_files),
    )

    # ======================================================
    # COMPLETE RAW DOCUMENTS
    # ======================================================

    raw_documents = (
        list_raw_document_content(
            project_id=project_id
        )
    )

    print(
        "Raw documents available:",
        len(raw_documents),
    )

    # ======================================================
    # DOCUMENTATION-ONLY MODE
    # ======================================================

    if not repo_metadata:

        print(
            "\n========== CURRICULUM MODE =========="
        )

        print(
            "Repository metadata: unavailable"
        )

        print(
            "Generating documentation-grounded "
            "curriculum."
        )

        print(
            "======================================\n"
        )

        return _generate_documentation_curriculum(
            project_id=project_id,
            raw_documents=raw_documents,
            developer_id=developer_id,
        )

    # ======================================================
    # REPOSITORY-AWARE MODE
    # ======================================================

    print(
        "\n========== REPOSITORY INTELLIGENCE =========="
    )

    # ------------------------------------------------------
    # Repository intelligence produces candidates.
    # It does NOT become the final curriculum.
    # ------------------------------------------------------

    repo_modules = build_repository_modules(
        repo_metadata,
        max_modules=12,
        start_step=1,
    )

    print(
        "Repository intelligence candidates:",
        len(repo_modules),
    )

    for module in repo_modules:

        print(
            f"- {module.get('title')} | "
            f"score={module.get('importance_score')} | "
            f"role={module.get('repository_role')} | "
            f"difficulty={module.get('difficulty')} | "
            f"sources={module.get('source_files', [])}"
        )

    print(
        "==============================================\n"
    )

    # ======================================================
    # BOUNDED CURRICULUM EVIDENCE
    # ======================================================

    project_evidence = _build_project_evidence(
        raw_documents=raw_documents,
        repo_modules=repo_modules,
        repo_metadata=repo_metadata,
        max_chars=12000,
        max_records=12,
        max_chars_per_record=1600,
    )

    print(
        "Curriculum evidence records:",
        len(project_evidence),
    )

    print(
        "Curriculum evidence characters:",
        sum(
            len(
                str(
                    item.get(
                        "evidence",
                        "",
                    )
                )
            )
            for item in project_evidence
        ),
    )

    for item in project_evidence:

        print(
            f"- {item.get('source_file')} | "
            f"role={item.get('evidence_role')}"
        )

    # ======================================================
    # DEVELOPER TWIN
    # ======================================================

    developer_profile = None

    if developer_id:

        developer_profile = get_twin(
            developer_id,
            project_id,
        )

        if developer_profile:

            print(
                "Developer Twin found: "
                "personalization available."
            )

        else:

            print(
                "Developer Twin not found: "
                "curriculum will remain project-focused."
            )

    # ======================================================
    # DYNAMIC CURRICULUM GENERATION
    # ======================================================

    print(
        "\n========== AI CURRICULUM GENERATION =========="
    )

    curriculum = generate_curriculum(
        project_id=project_id,
        repository_summary=repository_summary(
            repo_metadata
        ),
        repository_modules=repo_modules,
        project_evidence=project_evidence,
        developer_profile=developer_profile,
    )

    print(
        "AI curriculum response received."
    )

    raw_modules = curriculum.get(
        "modules",
        [],
    )

    print(
        "AI-generated module count:",
        len(raw_modules),
    )

    # ======================================================
    # NORMALIZATION + COURSE CONTENT
    # ======================================================

    modules = _normalize_curriculum_modules(
        project_id=project_id,
        modules=raw_modules,
        raw_documents=raw_documents,
    )

    print(
        "Normalized curriculum module count:",
        len(modules),
    )

    for module in modules:

        print(
            f"Step {module.get('step')}: "
            f"{module.get('title')} | "
            f"lessons={len(module.get('lessons', []))} | "
            f"sources={len(module.get('source_files', []))} | "
            f"course_content="
            f"{len(module.get('course_content', []))}"
        )

    print(
        "==============================================\n"
    )

    # ======================================================
    # FINAL RESPONSE
    # ======================================================

    result = {
        "project_id":
            project_id,

        "learning_path":
            modules,

        "repository_summary":
            repository_summary(
                repo_metadata
            ),

        "mode":
            "repository_aware",
    }

    # ======================================================
    # DEVELOPER TWIN PERSONALIZATION
    # ======================================================

    if developer_id:

        twin = get_twin(
            developer_id,
            project_id,
        )

        if twin:

            result["personalization_summary"] = (
                personalize_modules(
                    modules,
                    twin,
                )
            )

    return result


# ==========================================================
# LOCAL TEST
# ==========================================================


if __name__ == "__main__":

    import json

    result = generate_learning_path(
        "refund-service"
    )

    data_dir = (
        Path(__file__).parent.parent
        / "data"
    )

    output_path = (
        data_dir
        / "learning_path.json"
    )

    with open(
        output_path,
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            result,
            f,
            indent=2,
        )

    print(
        "\nGenerated learning path\n"
    )

    for item in result.get(
        "learning_path",
        [],
    ):

        print(
            f"Step {item.get('step')}: "
            f"{item.get('title')}"
        )

        print(
            f"Purpose: "
            f"{item.get('purpose', '')}"
        )

        print(
            f"Difficulty: "
            f"{item.get('difficulty', 'N/A')}"
        )

        print(
            f"Estimated time: "
            f"{item.get('estimated_minutes', 'N/A')} min"
        )

        print(
            f"Prerequisites: "
            f"{item.get('prerequisites', [])}"
        )

        print(
            f"Learning objectives: "
            f"{len(item.get('learning_objectives', []))}"
        )

        print(
            f"Lessons: "
            f"{len(item.get('lessons', []))}"
        )

        print(
            f"Source files: "
            f"{len(item.get('source_files', []))}"
        )

        print(
            f"Course content records: "
            f"{len(item.get('course_content', []))}"
        )

        print(
            "----------------------------------------"
        )

    print(
        f"Saved to: {output_path}"
    )