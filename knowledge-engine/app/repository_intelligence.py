"""
Repository Intelligence Layer.

Converts Repository Parser metadata into an explainable,
repository-aware onboarding structure.

Signals used:
- module structure
- internal dependency/import relationships
- number of dependent files
- module size
- module depth
- symbol counts
- entrypoints

Important:

This does NOT claim to discover the objectively correct learning order.

It derives a recommended onboarding sequence from repository evidence.

Important distinction:

Repository dependency != guaranteed learning prerequisite.

Import relationships are therefore treated as evidence first,
and learning prerequisites are exposed conservatively.
"""

import re

from typing import List, Optional

from collections import defaultdict


REFERENCE_PREFIXES = ("test", "tests")

EXAMPLE_PREFIXES = (
    "docs",
    "docs_src",
    "scripts",
    "examples",
    "example",
)


def _tier_for_path(path: str) -> str:
    first_segment = path.split("/")[0].lower()

    if first_segment.startswith(REFERENCE_PREFIXES):
        return "reference"

    if first_segment.startswith(EXAMPLE_PREFIXES):
        return "example"

    return "core"


def _infer_root_package(modules: List[dict]) -> Optional[str]:
    """
    Finds the repository's own top-level package.

    Example:
        fastapi
    """

    core_roots = [
        m["path"]
        for m in modules
        if (
            _tier_for_path(m["path"]) == "core"
            and "/" not in m["path"]
        )
    ]

    if not core_roots:
        return None

    return min(core_roots, key=len)


def _resolve_import_to_module(
    name: str,
    known_module_paths: set,
) -> Optional[str]:
    """
    Resolves:

        fastapi.dependencies.models

    to:

        fastapi/dependencies

    using progressively shorter dotted paths.
    """

    parts = name.split(".")

    for cut in range(len(parts), 0, -1):
        candidate = "/".join(parts[:cut])

        if candidate in known_module_paths:
            return candidate

    return None


def normalize_repository_metadata(metadata: dict) -> List[dict]:
    """
    Normalize Parser module records.

    Deduplication is based on PATH because module names may repeat.
    """

    raw_modules = (
        metadata.get("modules", [])
        if metadata
        else []
    )

    seen_paths = set()
    cleaned = []

    for m in raw_modules:
        path = m.get("path", "")

        if not path or path in seen_paths:
            continue

        seen_paths.add(path)

        important_files = (
            m.get("important_files", [])
            or []
        )

        cleaned.append({
            "name": m.get(
                "name",
                path.split("/")[-1],
            ),
            "path": path,
            "type": m.get(
                "type",
                "unknown",
            ),
            "file_count": len(important_files),
            "important_files": important_files,
            "tier": _tier_for_path(path),
            "depth": path.count("/") + 1,
        })

    return cleaned


def _find_owning_core_module(
    file_path: str,
    core_module_paths: set,
) -> Optional[str]:
    """
    Determines which core module owns a file.

    Uses the longest matching path so nested modules
    are handled correctly.
    """

    candidates = [
        path
        for path in core_module_paths
        if (
            file_path == path
            or file_path.startswith(path + "/")
        )
    ]

    if not candidates:
        return None

    return max(
        candidates,
        key=len,
    )


def _compute_dependency_graph(
    metadata: dict,
    core_module_paths: set,
    root_package: Optional[str],
):
    """
    Build evidence-based dependency relationships
    between core modules.

    Relationship direction:

        dependent module -> candidate prerequisite module

    Example:

        fastapi/routing imports fastapi/dependencies

    becomes:

        routing -> dependencies

    IMPORTANT:

    The repository root package is treated as the
    foundational entry point of the repository.

    Therefore it does not receive learning prerequisites,
    even if its implementation imports nested modules.

    Import relationships are still used as evidence.
    """

    prerequisites = defaultdict(set)

    if not root_package:
        return prerequisites

    for dep in metadata.get(
        "dependencies",
        [],
    ):
        importing_file = dep.get(
            "file",
            "",
        )

        imported_name = dep.get(
            "name",
            "",
        )

        if (
            not importing_file
            or not imported_name
        ):
            continue

        # Only consider imports from the
        # repository's own package.
        if not imported_name.startswith(
            root_package
        ):
            continue

        importer_module = _find_owning_core_module(
            importing_file,
            core_module_paths,
        )

        if not importer_module:
            continue

        target_module = _resolve_import_to_module(
            imported_name,
            core_module_paths,
        )

        if not target_module:
            continue

        # Ignore self-dependencies.
        if target_module == importer_module:
            continue

        # --------------------------------------------------
        # ROOT PACKAGE PROTECTION
        # --------------------------------------------------
        #
        # The repository root package is the foundation
        # from which onboarding begins.
        #
        # Its internal imports are implementation evidence,
        # not learner prerequisites.
        #
        # Example:
        #
        #     fastapi/__init__.py
        #         imports middleware
        #
        # does NOT mean:
        #
        #     Middleware -> FastAPI
        #
        # is required for learning.
        #
        # Therefore the root package never receives
        # prerequisite edges.
        # --------------------------------------------------

        if importer_module == root_package:
            continue

        prerequisites[importer_module].add(
            target_module
        )

    # --------------------------------------------------
    # CYCLE-SAFE LEARNING PREREQUISITES
    # --------------------------------------------------

    module_depth = {
        path: path.count("/") + 1
        for path in core_module_paths
    }

    def _find_strongly_connected_components(graph):
        """
        Tarjan's algorithm.

        Returns strongly connected components where every
        module is reachable from every other module.
        """

        index = 0
        indices = {}
        lowlinks = {}
        stack = []
        on_stack = set()
        components = []

        def strong_connect(node):
            nonlocal index

            indices[node] = index
            lowlinks[node] = index
            index += 1

            stack.append(node)
            on_stack.add(node)

            for target in graph.get(
                node,
                set(),
            ):
                if target not in indices:
                    strong_connect(target)

                    lowlinks[node] = min(
                        lowlinks[node],
                        lowlinks[target],
                    )

                elif target in on_stack:
                    lowlinks[node] = min(
                        lowlinks[node],
                        indices[target],
                    )

            if lowlinks[node] == indices[node]:
                component = set()

                while True:
                    current = stack.pop()

                    on_stack.remove(current)
                    component.add(current)

                    if current == node:
                        break

                components.append(component)

        for node in graph:
            if node not in indices:
                strong_connect(node)

        return components

    components = _find_strongly_connected_components(
        prerequisites
    )

    for component in components:

        # A component with one node is only cyclic if it
        # contains a self-edge. Self-edges were already removed.
        if len(component) <= 1:
            continue

        internal_edges = []

        for importer in component:
            for target in prerequisites.get(
                importer,
                set(),
            ):
                if target in component:
                    internal_edges.append(
                        (
                            importer,
                            target,
                        )
                    )

        # Remove all internal cycle edges first.
        for importer, target in internal_edges:
            prerequisites[importer].discard(
                target
            )

        # Reintroduce only relationships that clearly
        # point from deeper modules toward shallower ones.
        for importer, target in internal_edges:

            importer_depth = module_depth.get(
                importer,
                1,
            )

            target_depth = module_depth.get(
                target,
                1,
            )

            if target_depth < importer_depth:
                prerequisites[importer].add(
                    target
                )

    # --------------------------------------------------
    # FINAL ROOT PACKAGE SAFETY
    # --------------------------------------------------

    if root_package:
        prerequisites.pop(
            root_package,
            None,
        )

    return prerequisites


def _compute_dependents(
    metadata: dict,
    core_module_paths: set,
    root_package: Optional[str],
) -> dict:
    """
    Count distinct repository files that depend on each
    core module.

    This is genuine usage evidence.
    """

    dependents_files = defaultdict(set)

    if not root_package:
        return {}

    for dep in metadata.get(
        "dependencies",
        [],
    ):
        name = dep.get(
            "name",
            "",
        )

        if not name.startswith(
            root_package
        ):
            continue

        target_module = _resolve_import_to_module(
            name,
            core_module_paths,
        )

        if not target_module:
            continue

        importing_file = dep.get(
            "file",
            "",
        )

        if (
            importing_file.startswith(
                target_module + "/"
            )
            or importing_file == target_module
        ):
            continue

        dependents_files[
            target_module
        ].add(
            importing_file
        )

    return {
        path: len(files)
        for path, files in dependents_files.items()
    }


def _compute_symbol_counts(
    metadata: dict,
    core_module_paths: set,
) -> dict:
    """
    Count functions/classes attributed to each core module.
    """

    sorted_paths = sorted(
        core_module_paths,
        key=len,
        reverse=True,
    )

    counts = defaultdict(int)

    for entry in metadata.get(
        "symbols",
        [],
    ):
        file_path = entry.get(
            "file",
            "",
        )

        owning = None

        for module_path in sorted_paths:
            if (
                file_path == module_path
                or file_path.startswith(
                    module_path + "/"
                )
            ):
                owning = module_path
                break

        if owning:
            counts[owning] += len(
                entry.get(
                    "symbols",
                    [],
                )
            )

    return dict(counts)


def _humanize_name(name: str) -> str:
    SPECIAL = {
        "openapi": "OpenAPI",
        "sql": "SQL",
        "api": "API",
        "cli": "CLI",
        "sse": "SSE",
        "compat": "Compatibility",
        "fastapi": "FastAPI",
    }

    words = re.split(
        r"[_\-]+",
        name.lstrip("_"),
    )

    return " ".join(
        SPECIAL.get(
            word.lower(),
            word.capitalize(),
        )
        for word in words
    )


def _infer_module_role(module: dict) -> str:
    """
    Infer a broad pedagogical role from repository structure.

    Role hierarchy:
        foundation
        core
        infrastructure
        interface
        specialized

    The role is only one signal used by the
    learning-path engine. It is NOT treated as ground truth.
    """

    name = module.get(
        "name",
        "",
    ).lower()

    path = module.get(
        "path",
        "",
    ).lower()

    basename = path.split("/")[-1]

    text = f"{name} {basename}"

    # --------------------------------------------------
    # FOUNDATION
    # --------------------------------------------------

    if (
        path.count("/") == 0
        or name in {
            "core",
            "base",
            "common",
            "foundation",
        }
    ):
        return "foundation"

    # --------------------------------------------------
    # INFRASTRUCTURE
    # --------------------------------------------------

    if any(
        keyword in text
        for keyword in [
            "middleware",
            "database",
            "db",
            "storage",
            "cache",
            "logging",
            "logger",
            "config",
            "configuration",
            "compat",
            "adapter",
            "integration",
            "interop",
        ]
    ):
        return "infrastructure"

    # --------------------------------------------------
    # DEPENDENCY / RESOLUTION
    # --------------------------------------------------

    if any(
        keyword in text
        for keyword in [
            "dependenc",
            "inject",
            "resolver",
        ]
    ):
        return "core"

    # --------------------------------------------------
    # SCHEMA / MODEL / DATA
    # --------------------------------------------------

    if any(
        keyword in text
        for keyword in [
            "schema",
            "model",
            "models",
            "validation",
            "serializer",
            "serialization",
        ]
    ):
        return "core"

    # --------------------------------------------------
    # INTERFACE / API
    # --------------------------------------------------

    if any(
        keyword in text
        for keyword in [
            "api",
            "route",
            "routing",
            "endpoint",
            "controller",
            "view",
        ]
    ):
        return "interface"

    # --------------------------------------------------
    # SECURITY / AUTH
    # --------------------------------------------------

    if any(
        keyword in text
        for keyword in [
            "security",
            "auth",
            "authentication",
            "authorization",
            "permission",
        ]
    ):
        return "specialized"

    # --------------------------------------------------
    # DEFAULT
    # --------------------------------------------------

    return "core"


def _difficulty_for_module(module: dict) -> str:
    """
    Estimate learning difficulty from repository evidence.

    Difficulty is a heuristic, not a claim about the learner.
    """

    score = 0

    symbol_count = module.get(
        "symbol_count",
        0,
    )

    file_count = module.get(
        "file_count",
        0,
    )

    dependents_count = module.get(
        "dependents_count",
        0,
    )

    depth = module.get(
        "depth",
        1,
    )

    role = module.get(
        "repository_role",
        "core",
    )

    # Size / implementation complexity.
    if file_count >= 15:
        score += 2

    elif file_count >= 7:
        score += 1

    # Number of symbols.
    if symbol_count >= 100:
        score += 2

    elif symbol_count >= 30:
        score += 1

    # Repository coupling.
    if dependents_count >= 50:
        score += 2

    elif dependents_count >= 10:
        score += 1

    # Deeper modules generally require more context.
    if depth >= 3:
        score += 1

    # Specialized modules usually require more
    # domain-specific understanding.
    if role == "specialized":
        score += 1

    if score >= 5:
        return "hard"

    if score >= 2:
        return "medium"

    return "easy"


def _estimate_effort_minutes(
    file_count: int,
    symbol_count: int = 0,
    dependents_count: int = 0,
    difficulty: str = "medium",
) -> int:
    """
    Estimate onboarding effort using repository evidence.

    Signals:
    - number of files
    - number of functions/classes
    - repository coupling
    - inferred difficulty

    This is an estimate for onboarding effort, not
    an estimate of implementation time.
    """

    minutes = 10

    # --------------------------------------------------
    # FILE COMPLEXITY
    # --------------------------------------------------

    if file_count >= 20:
        minutes += 15

    elif file_count >= 10:
        minutes += 10

    elif file_count >= 5:
        minutes += 5

    # --------------------------------------------------
    # SYMBOL COMPLEXITY
    # --------------------------------------------------

    if symbol_count >= 150:
        minutes += 15

    elif symbol_count >= 75:
        minutes += 10

    elif symbol_count >= 30:
        minutes += 5

    # --------------------------------------------------
    # REPOSITORY COUPLING
    # --------------------------------------------------

    if dependents_count >= 100:
        minutes += 10

    elif dependents_count >= 50:
        minutes += 5

    elif dependents_count >= 10:
        minutes += 3

    # --------------------------------------------------
    # DIFFICULTY
    # --------------------------------------------------

    if difficulty == "hard":
        minutes += 10

    elif difficulty == "medium":
        minutes += 5

    # --------------------------------------------------
    # Keep estimates bounded and deterministic.
    # --------------------------------------------------

    return min(
        max(minutes, 10),
        90,
    )


def score_core_modules(
    core_modules: List[dict],
    dependents: dict,
    symbol_counts: dict,
) -> List[dict]:
    """
    Score core modules using multiple repository signals.

    Signals:
    - repository usage / dependents
    - module size
    - module depth
    - inferred repository role
    - symbol count

    The score represents repository importance.

    It does NOT represent an objectively correct
    learning order.
    """

    if not core_modules:
        return []

    max_files = max(
        (
            m.get("file_count", 0)
            for m in core_modules
        ),
        default=0,
    ) or 1

    max_depth = max(
        (
            m.get("depth", 1)
            for m in core_modules
        ),
        default=1,
    ) or 1

    max_dependents = (
        max(
            dependents.values()
        )
        if dependents
        else 0
    )

    max_symbols = max(
        (
            symbol_counts.get(
                m["path"],
                0,
            )
            for m in core_modules
        ),
        default=0,
    ) or 1

    role_weights = {
        "foundation": 1.00,
        "core": 0.90,
        "interface": 0.75,
        "infrastructure": 0.65,
        "specialized": 0.55,
    }

    scored = []

    for m in core_modules:

        dep_count = dependents.get(
            m["path"],
            0,
        )

        sym_count = symbol_counts.get(
            m["path"],
            0,
        )

        file_signal = (
            m.get("file_count", 0)
            / max_files
        )

        depth_signal = (
            1
            - (
                (m.get("depth", 1) - 1)
                / max_depth
            )
        )

        dependents_signal = (
            dep_count / max_dependents
            if max_dependents
            else 0
        )

        symbol_signal = (
            sym_count / max_symbols
            if max_symbols
            else 0
        )

        role = _infer_module_role(m)

        role_signal = role_weights.get(
            role,
            0.5,
        )

        importance_score = round(
            0.40 * dependents_signal
            + 0.20 * file_signal
            + 0.15 * depth_signal
            + 0.10 * symbol_signal
            + 0.15 * role_signal,
            3,
        )

        evidence = [
            f"{m.get('file_count', 0)} files in this module"
        ]

        if dep_count > 0:
            evidence.insert(
                0,
                (
                    f"referenced by {dep_count} "
                    "files across the repository "
                    "(real import analysis)"
                ),
            )

        if sym_count > 0:
            evidence.append(
                f"defines {sym_count} "
                "functions/classes"
            )

        evidence.append(
            f"path depth {m.get('depth', 1)} — "
            + (
                "top-level, likely foundational"
                if m.get("depth", 1) <= 1
                else "nested subpackage"
            )
        )

        evidence.append(
            f"inferred repository role: {role}"
        )

        # --------------------------------------------------
        # CONFIDENCE
        # --------------------------------------------------

        evidence_signals = 0

        if dep_count > 0:
            evidence_signals += 1

        if m.get("file_count", 0) > 0:
            evidence_signals += 1

        if sym_count > 0:
            evidence_signals += 1

        if m.get("depth", 1) >= 1:
            evidence_signals += 1

        if role:
            evidence_signals += 1

        if (
            evidence_signals >= 4
            and (
                dep_count >= 10
                or sym_count >= 30
                or file_signal >= 0.3
            )
        ):
            confidence = "high"

        elif evidence_signals >= 3:
            confidence = "medium"

        else:
            confidence = "low"

        # --------------------------------------------------
        # DIFFICULTY
        # --------------------------------------------------

        enriched_module = {
            **m,
            "repository_role": role,
            "dependents_count": dep_count,
            "symbol_count": sym_count,
        }

        difficulty = _difficulty_for_module(
            enriched_module
        )

        # --------------------------------------------------
        # ESTIMATED EFFORT
        #
        # IMPORTANT:
        # This is where estimated_minutes is now ALWAYS
        # created before build_repository_modules()
        # tries to read it.
        # --------------------------------------------------

        estimated_minutes = _estimate_effort_minutes(
            file_count=m.get(
                "file_count",
                0,
            ),
            symbol_count=sym_count,
            dependents_count=dep_count,
            difficulty=difficulty,
        )

        scored.append({
            **m,

            "dependents_count":
                dep_count,

            "symbol_count":
                sym_count,

            "repository_role":
                role,

            "importance_score":
                importance_score,

            "evidence":
                evidence,

            "confidence":
                confidence,

            "difficulty":
                difficulty,

            "estimated_minutes":
                estimated_minutes,
        })

    scored.sort(
        key=lambda x: (
            -x["importance_score"],
            x["depth"],
            x["path"],
        )
    )

    return scored


def _order_by_prerequisites(
    selected_modules: List[dict],
    prerequisites: dict,
    root_package: Optional[str] = None,
) -> List[dict]:
    """
    Produce a pedagogical ordering for selected repository modules.

    Hard constraints:

    1. The repository root package comes first.

    2. A selected repository dependency must appear before
       the dependent module when that dependency is also selected.

    Soft ordering signals:

    1. repository role
    2. importance score
    3. module depth
    4. deterministic path ordering

    The repository root package is always treated as the
    foundational onboarding anchor.
    """

    selected_paths = {
        m["path"]
        for m in selected_modules
    }

    remaining = {
        m["path"]: m
        for m in selected_modules
    }

    ordered = []

    role_priority = {
        "foundation": 0,
        "core": 1,
        "infrastructure": 2,
        "interface": 3,
        "specialized": 4,
    }

    while remaining:

        ready = []

        for path, module in remaining.items():

            # --------------------------------------------------
            # ROOT PACKAGE
            # --------------------------------------------------

            if (
                root_package
                and path == root_package
            ):
                ready.append(module)
                continue

            deps = prerequisites.get(
                path,
                set(),
            )

            selected_deps = (
                deps & selected_paths
            )

            if all(
                dep not in remaining
                for dep in selected_deps
            ):
                ready.append(module)

        # --------------------------------------------------
        # CYCLE HANDLING
        # --------------------------------------------------

        if not ready:
            ready = list(
                remaining.values()
            )

        # --------------------------------------------------
        # SOFT PEDAGOGICAL ORDERING
        # --------------------------------------------------

        ready.sort(
            key=lambda m: (
                # Root package always wins.
                0
                if (
                    root_package
                    and m["path"] == root_package
                )
                else 1,

                role_priority.get(
                    m.get(
                        "repository_role",
                        "core",
                    ),
                    1,
                ),

                -m.get(
                    "importance_score",
                    0,
                ),

                m.get(
                    "depth",
                    1,
                ),

                m.get(
                    "path",
                    "",
                ),
            )
        )

        chosen = ready[0]

        ordered.append(
            chosen
        )

        remaining.pop(
            chosen["path"]
        )

    return ordered


def _purpose_for_module(
    module: dict,
) -> str:
    """
    Deterministic purpose hints based on repository structure.

    This is intentionally conservative.
    """

    name = module["name"].lower()
    path = module["path"].lower()

    if "dependency" in name:
        return (
            "Understand dependency handling and "
            "how reusable request logic fits into "
            "the framework."
        )

    if (
        "routing" in name
        or "route" in name
    ):
        return (
            "Understand how requests are mapped "
            "to application operations."
        )

    if "security" in name:
        return (
            "Understand authentication and authorization "
            "mechanisms provided by the framework."
        )

    if (
        "params" in name
        or "parameter" in name
    ):
        return (
            "Understand how request parameters and "
            "validation inputs are represented."
        )

    if "response" in name:
        return (
            "Understand response handling and serialization."
        )

    if "openapi" in name:
        return (
            "Understand API schema generation and "
            "OpenAPI integration."
        )

    if path == "fastapi":
        return (
            "Understand the core framework entry point "
            "and foundational application behavior."
        )

    return (
        f"Understand the {module['name']} module "
        "and how it fits into the repository."
    )


def _learning_objectives_for_module(
    module: dict,
) -> List[str]:
    """
    Generate deterministic, repository-aware learning objectives.

    Objectives are based on the module's inferred role and
    structural evidence. They are intentionally conservative:
    the function describes what the learner should understand,
    rather than pretending to know exact implementation details.
    """

    raw_name = module.get(
        "name",
        "",
    )

    name = _humanize_name(
        raw_name
    )

    path = module.get(
        "path",
        "",
    ).lower()

    role = module.get(
        "repository_role",
        "core",
    )

    objectives = []

    # --------------------------------------------------
    # ROLE-BASED OBJECTIVE
    # --------------------------------------------------

    role_objectives = {
        "foundation": (
            f"Understand the role of {name} as a foundational "
            "part of the repository."
        ),

        "core": (
            f"Understand the core responsibilities of the "
            f"{name} module."
        ),

        "infrastructure": (
            f"Understand how {name} supports the repository's "
            "underlying infrastructure."
        ),

        "interface": (
            f"Understand how {name} exposes or connects "
            "application-facing functionality."
        ),

        "specialized": (
            f"Understand the specialized responsibilities "
            f"provided by {name}."
        ),
    }

    objectives.append(
        role_objectives.get(
            role,
            f"Understand the role and responsibilities of "
            f"{name} in the repository.",
        )
    )

    # --------------------------------------------------
    # DOMAIN-SPECIFIC OBJECTIVES
    # --------------------------------------------------

    if "dependency" in path:

        objectives.extend([
            "Understand how dependencies are represented "
            "and resolved.",

            "Understand how dependency-related logic "
            "supports reusable application behavior.",
        ])

    elif "security" in path or "auth" in path:

        objectives.extend([
            "Understand the repository's authentication "
            "and authorization mechanisms.",

            "Understand how security-related components "
            "connect to application behavior.",
        ])

    elif "openapi" in path:

        objectives.extend([
            "Understand how API schemas are generated.",

            "Understand how OpenAPI information is connected "
            "to the framework's API behavior.",
        ])

    elif "middleware" in path:

        objectives.extend([
            "Understand where middleware participates in "
            "the application request/response flow.",

            "Understand the responsibilities of the "
            "middleware components present in the repository.",
        ])

    elif "routing" in path or "route" in path:

        objectives.extend([
            "Understand how incoming requests are mapped "
            "to application operations.",

            "Understand the main routing components and "
            "their relationships.",
        ])

    elif "compat" in path:

        objectives.extend([
            "Understand why compatibility abstractions exist.",

            "Understand how compatibility logic isolates "
            "version- or environment-specific behavior.",
        ])

    else:

        objectives.extend([
            f"Identify the main components implemented in "
            f"{name}.",

            f"Understand how {name} relates to other "
            "repository modules.",
        ])

    # --------------------------------------------------
    # EVIDENCE-BASED OBJECTIVES
    # --------------------------------------------------

    if module.get("dependents_count", 0) >= 10:

        objectives.append(
            "Understand how other repository components "
            "depend on this module."
        )

    if module.get("symbol_count", 0) >= 30:

        objectives.append(
            "Identify the major functions and classes "
            "that define this module's behavior."
        )

    # Remove duplicates while preserving order.
    unique = []

    for objective in objectives:

        if objective not in unique:
            unique.append(objective)

    return unique[:5]


def build_repository_modules(
    metadata: dict,
    max_modules: int = 6,
    start_step: int = 1,
) -> List[dict]:
    """
    Build repository-aware learning modules.

    The repository parser provides structural evidence such as:
    - module structure
    - dependency/import relationships
    - dependent file counts
    - symbol counts
    - module depth

    This function converts that evidence into a recommended
    onboarding sequence.

    Important distinction:

        repository dependency
        !=
        guaranteed learning prerequisite

    Import relationships are therefore retained as evidence,
    while the public `prerequisites` field only exposes
    repository dependencies compatible with the final
    pedagogical ordering.
    """

    # --------------------------------------------------
    # NORMALIZE REPOSITORY METADATA
    # --------------------------------------------------

    normalized = normalize_repository_metadata(
        metadata
    )

    # --------------------------------------------------
    # IDENTIFY CORE MODULES
    # --------------------------------------------------

    core = [
        m
        for m in normalized
        if m["tier"] == "core"
    ]

    core_paths = {
        m["path"]
        for m in core
    }

    # --------------------------------------------------
    # IDENTIFY ROOT PACKAGE
    # --------------------------------------------------

    root_package = _infer_root_package(
        normalized
    )

    # --------------------------------------------------
    # REPOSITORY EVIDENCE
    # --------------------------------------------------

    dependents = _compute_dependents(
        metadata,
        core_paths,
        root_package,
    )

    prerequisites = _compute_dependency_graph(
        metadata,
        core_paths,
        root_package,
    )

    symbol_counts = _compute_symbol_counts(
        metadata,
        core_paths,
    )

    # --------------------------------------------------
    # IMPORTANCE SCORING
    # --------------------------------------------------

    ranked = score_core_modules(
        core,
        dependents,
        symbol_counts,
    )

    # Select only the strongest repository modules
    # for the current learning path.
    selected = ranked[:max_modules]

    # --------------------------------------------------
    # PEDAGOGICAL ORDER
    # --------------------------------------------------

    ordered = _order_by_prerequisites(
        selected,
        prerequisites,
        root_package=root_package,
    )

    # --------------------------------------------------
    # BUILD FINAL LEARNING MODULES
    # --------------------------------------------------

    result = []

    # The final pedagogical order is authoritative
    # for determining whether a dependency can appear
    # as a learning prerequisite.

    ordered_paths = [
        m["path"]
        for m in ordered
    ]

    position = {
        path: index
        for index, path in enumerate(
            ordered_paths
        )
    }

    for i, module in enumerate(
        ordered
    ):

        path = module["path"]

        # --------------------------------------------------
        # PEDAGOGICAL PREREQUISITES
        # --------------------------------------------------

        direct_prerequisites = []

        # Root package is always foundational.
        if (
            root_package
            and path == root_package
        ):
            direct_prerequisites = []

        else:

            for candidate in prerequisites.get(
                path,
                set(),
            ):

                if candidate not in position:
                    continue

                if position[candidate] < position[path]:
                    direct_prerequisites.append(
                        candidate
                    )

        direct_prerequisites.sort(
            key=lambda p: position[p]
        )

        prerequisite_names = [
            _humanize_name(
                p.split("/")[-1]
            )
            for p in direct_prerequisites
        ]

        # --------------------------------------------------
        # EVIDENCE
        # --------------------------------------------------

        evidence = list(
            module.get(
                "evidence",
                [],
            )
        )

        if prerequisite_names:
            evidence.append(
                "repository dependency evidence "
                "indicates these modules are relevant "
                "prerequisites: "
                + ", ".join(
                    prerequisite_names
                )
            )

        # --------------------------------------------------
        # FINAL MODULE CONTRACT
        # --------------------------------------------------

        difficulty = module.get(
            "difficulty",
            "medium",
        )

        # IMPORTANT:
        # Use the value calculated by score_core_modules().
        #
        # The fallback makes this function safe even if
        # another caller supplies a module without the field.
        estimated_minutes = module.get(
            "estimated_minutes"
        )

        if not isinstance(
            estimated_minutes,
            int,
        ):
            estimated_minutes = _estimate_effort_minutes(
                file_count=module.get(
                    "file_count",
                    0,
                ),
                symbol_count=module.get(
                    "symbol_count",
                    0,
                ),
                dependents_count=module.get(
                    "dependents_count",
                    0,
                ),
                difficulty=difficulty,
            )

        result.append({
            "step":
                start_step + i,

            "title":
                _humanize_name(
                    module["name"]
                ),

            "description":
                _purpose_for_module(
                    module
                ),

            "purpose":
                _purpose_for_module(
                    module
                ),

            "learning_objectives":
                _learning_objectives_for_module({
                    **module,
                    "repository_role":
                        module.get(
                            "repository_role",
                            "core",
                        ),
                }),

            "difficulty":
                difficulty,

            "estimated_minutes":
                estimated_minutes,

            "sources":
                [path],

            "evidence":
                evidence,

            "confidence":
                module.get(
                    "confidence",
                    "medium",
                ),

            "importance_score":
                module.get(
                    "importance_score",
                    0,
                ),

            "repository_role":
                module.get(
                    "repository_role",
                    "core",
                ),

            "prerequisites":
                prerequisite_names,

            "dependents_count":
                module.get(
                    "dependents_count",
                    0,
                ),

            "symbol_count":
                module.get(
                    "symbol_count",
                    0,
                ),
        })

    return result


def repository_summary(
    metadata: dict,
) -> Optional[dict]:

    normalized = normalize_repository_metadata(
        metadata
    )

    if not normalized:
        return None

    by_tier = {}

    for module in normalized:

        tier = module["tier"]

        by_tier[tier] = (
            by_tier.get(
                tier,
                0,
            )
            + 1
        )

    return {
        "total_modules_found":
            len(normalized),

        "core_modules":
            by_tier.get(
                "core",
                0,
            ),

        "reference_modules":
            by_tier.get(
                "reference",
                0,
            ),

        "example_modules":
            by_tier.get(
                "example",
                0,
            ),

        "total_dependencies_analyzed":
            len(
                metadata.get(
                    "dependencies",
                    [],
                )
            ),

        "entrypoints_found":
            len(
                metadata.get(
                    "entrypoints",
                    [],
                )
            ),
    }