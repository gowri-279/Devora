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
        return json.dumps({
            "modules": [
                {
                    "title": "Project Overview",
                    "description": "Understand the project structure, purpose, and key technologies used.",
                    "difficulty": "easy",
                    "estimated_minutes": 20,
                    "learning_objectives": [
                        "Understand the overall project architecture",
                        "Identify key components and their relationships",
                    ],
                    "prerequisites": [],
                    "lessons": [
                        {
                            "concept": "Project Structure",
                            "explanation": "This project is composed of multiple services working together to provide AI-powered developer onboarding.",
                            "why_it_matters": "Understanding the overall structure helps you navigate the codebase efficiently.",
                            "how_project_implements_it": "Services are separated into backend, knowledge-engine, ai-integration, and repository-parser.",
                            "repository_exploration": ["Explore the root directory to understand the service layout."],
                            "key_takeaway": "Each service has a clear single responsibility.",
                            "sources": [],
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

