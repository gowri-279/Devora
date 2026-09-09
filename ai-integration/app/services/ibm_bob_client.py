import json
import os
import subprocess

from app.config import BOB_API_KEY, DEVORA_BOB_MODE


class IBMBobClient:
    """
    Client responsible for communicating with IBM Bob through Bob Shell.
    """

    def __init__(
        self,
        api_key: str | None = None,
    ):
        self.api_key = api_key or BOB_API_KEY

    def generate(self, prompt: str) -> str:
        # ----------------------------------------------------------------
        # Mock mode — allows the full pipeline to run without Bob CLI.
        # Activated when DEVORA_BOB_MODE=mock or BOB_API_KEY is absent.
        # ----------------------------------------------------------------
        if DEVORA_BOB_MODE == "mock" or not self.api_key:
            return self._mock_response(prompt)

        # Live mode — requires bob CLI on PATH with a valid BOB_API_KEY.

        env = os.environ.copy()
        env["BOB_API_KEY"] = self.api_key

        try:
            result = subprocess.run(
                [
                    "bob",
                    "run",
                    "--format",
                    "json",
                    "--mode",
                    "ask",
                    "--max-turns",
                    "1",
                    "--disable-tool-groups",
                    "read,edit,execute,mcp,skill,todo,subagent,mode",
                      prompt,
                ],
                capture_output=True,
                text=True,
                timeout=180,
                env=env,
                cwd=os.getcwd(),
                check=False,
            )

        except subprocess.TimeoutExpired as error:
            raise RuntimeError(
                "IBM Bob request timed out."
            ) from error

        except FileNotFoundError as error:
            raise RuntimeError(
                "Bob Shell was not found. Make sure `bob` is installed "
                "and available on PATH."
            ) from error

        if result.returncode != 0:
            message = (
                result.stderr.strip()
                or result.stdout.strip()
                or "Unknown IBM Bob error."
            )

            raise RuntimeError(
                f"IBM Bob request failed: {message}"
            )

        stdout = result.stdout.strip()

        if not stdout:
            raise RuntimeError(
                "IBM Bob returned an empty response."
            )

        response = self._parse_bob_output(stdout)

        if response.get("status") != "success":
            raise RuntimeError(
                "IBM Bob returned unsuccessful status: "
                f"{response.get('status')}"
            )

        last_message = response.get("last_message")

        if not isinstance(last_message, str) or not last_message.strip():
            raise RuntimeError(
                "IBM Bob returned no usable response."
            )

        return last_message.strip()

    @staticmethod
    def _mock_response(prompt: str) -> str:
        """
        Deterministic mock response used when DEVORA_BOB_MODE=mock.
        Returns valid JSON that satisfies both the assessment evaluator
        and the curriculum service parsers.
        """
        prompt_lower = prompt.lower()

        # Curriculum prompts must always receive the curriculum mock,
        # even when the supplied project evidence contains assessment text.
        if "curriculum generator" not in prompt_lower and (
            "evaluate" in prompt_lower
            or "assessment" in prompt_lower
            or "domain_scores" in prompt_lower
        ):
            return json.dumps({
                "evaluator": "mock",
                "domain_scores": {
                    "APIs": {"score": 72, "confidence": "MEDIUM", "evidence": "Mock: IBM Bob evaluation unavailable (DEVORA_BOB_MODE=mock)."},
                    "Architecture": {"score": 68, "confidence": "MEDIUM", "evidence": "Mock: IBM Bob evaluation unavailable (DEVORA_BOB_MODE=mock)."},
                    "Database": {"score": 65, "confidence": "MEDIUM", "evidence": "Mock: IBM Bob evaluation unavailable (DEVORA_BOB_MODE=mock)."},
                    "Security": {"score": 70, "confidence": "MEDIUM", "evidence": "Mock: IBM Bob evaluation unavailable (DEVORA_BOB_MODE=mock)."},
                },
                "cross_domain_evidence": [
                    "Mock evaluation: set DEVORA_BOB_MODE=live and provide BOB_API_KEY for real IBM Bob analysis."
                ],
                "overall_score": 69,
                "summary": "Mock evaluation completed. Set DEVORA_BOB_MODE=live with a valid BOB_API_KEY for real IBM Bob assessment analysis.",
                "next_focus": "Database",
            })

        # Curriculum generation mock
        # Return a repository-specific curriculum for the demo.
        return json.dumps({
            "modules": [
                {
                    "title": "FastAPI-101 Project Architecture",
                    "description": "Understand how the FastAPI-101 application is structured, including its application layer, services, configuration, models, database, authentication, and tests.",
                    "difficulty": "easy",
                    "estimated_minutes": 25,
                    "learning_objectives": [
                        "Understand the FastAPI-101 application structure",
                        "Identify how services, models, configuration, and database components interact",
                        "Navigate the authentication and testing layers",
                    ],
                    "prerequisites": [],
                    "lessons": [
                        {
                            "concept": "Application Structure",
                            "explanation": "FastAPI-101 separates application concerns into focused modules such as services, configuration, models, database, authentication, and tests.",
                            "why_it_matters": "Understanding these boundaries helps developers navigate and safely modify the project.",
                            "how_project_implements_it": "The repository contains an app layer with services.py, config.py, models.py, database.py, auth.py, and related application modules, alongside a dedicated tests directory.",
                            "repository_exploration": [
                                "Explore the app directory.",
                                "Open services.py, config.py, models.py, database.py, and auth.py.",
                                "Review the tests directory to understand expected behavior."
                            ],
                            "key_takeaway": "FastAPI-101 uses a modular application structure that separates core responsibilities.",
                            "sources": [
                                "app/services.py",
                                "app/config.py",
                                "app/models.py",
                                "app/database.py",
                                "app/auth.py",
                                "tests"
                            ],
                        }
                    ],
                },
                {
                    "title": "Services, Database & Authentication",
                    "description": "Learn how business logic, persistence, and authentication work together in FastAPI-101.",
                    "difficulty": "medium",
                    "estimated_minutes": 30,
                    "learning_objectives": [
                        "Understand the service layer",
                        "Trace database interactions",
                        "Understand authentication responsibilities",
                    ],
                    "prerequisites": ["FastAPI-101 Project Architecture"],
                    "lessons": [
                        {
                            "concept": "Service and Persistence Flow",
                            "explanation": "Requests are handled through application services that coordinate models and database operations.",
                            "why_it_matters": "Tracing this flow makes it easier to debug and extend application behavior.",
                            "how_project_implements_it": "The repository contains dedicated service, model, and database modules.",
                            "repository_exploration": [
                                "Trace a service method into the model and database layers.",
                                "Inspect authentication-related code."
                            ],
                            "key_takeaway": "Business logic, persistence, and authentication are separated into dedicated components.",
                            "sources": [
                                "app/services.py",
                                "app/models.py",
                                "app/database.py",
                                "app/auth.py"
                            ],
                        }
                    ],
                },
                {
                    "title": "Testing & Project Workflows",
                    "description": "Understand how FastAPI-101 verifies behavior and organizes development workflows.",
                    "difficulty": "medium",
                    "estimated_minutes": 20,
                    "learning_objectives": [
                        "Understand the project's test organization",
                        "Identify how application behavior is validated",
                        "Explore repository development workflows",
                    ],
                    "prerequisites": ["Services, Database & Authentication"],
                    "lessons": [
                        {
                            "concept": "Repository Testing",
                            "explanation": "FastAPI-101 includes dedicated tests for application services and behavior.",
                            "why_it_matters": "Tests provide a safety net when changing project functionality.",
                            "how_project_implements_it": "The tests directory contains service-focused tests such as test_item_service.py and test_category_service.py.",
                            "repository_exploration": [
                                "Open tests/test_item_service.py.",
                                "Open tests/test_category_service.py.",
                                "Review the GitHub workflow configuration."
                            ],
                            "key_takeaway": "The repository combines modular code with focused automated tests.",
                            "sources": [
                                "tests/test_item_service.py",
                                "tests/test_category_service.py",
                                ".github/workflows"
                            ],
                        }
                    ],
                }
            ]
        })

    @staticmethod
    def _parse_bob_output(stdout: str) -> dict:
        """
        Parse Bob Shell JSON output.

        Bob Shell's --format json normally returns one final
        JSON result object. We also tolerate JSONL/multiple
        JSON objects for compatibility with different versions.
        """

        # -----------------------------------------------------
        # 1. Entire stdout is one JSON object
        # -----------------------------------------------------
        try:
            parsed = json.loads(stdout)

            if isinstance(parsed, dict):
                return parsed

        except json.JSONDecodeError:
            pass

        # -----------------------------------------------------
        # 2. Multiple JSON lines / JSONL
        # -----------------------------------------------------
        json_objects = []

        for line in stdout.splitlines():
            line = line.strip()

            if not line:
                continue

            try:
                parsed = json.loads(line)

            except json.JSONDecodeError:
                continue

            if isinstance(parsed, dict):
                json_objects.append(parsed)

        if json_objects:

            # Prefer a successful result containing last_message.
            for obj in reversed(json_objects):
                if (
                    obj.get("status") == "success"
                    and isinstance(
                        obj.get("last_message"),
                        str,
                    )
                    and obj.get("last_message").strip()
                ):
                    return obj

            return json_objects[-1]

        preview = stdout[:1200]

        raise RuntimeError(
            "IBM Bob returned output that could not be parsed as JSON. "
            f"Output preview: {preview}"
        )

