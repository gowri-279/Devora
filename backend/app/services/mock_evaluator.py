from app.services.evaluator import AssessmentEvaluator, EvaluationResult


class MockEvaluator(AssessmentEvaluator):
    """
    Deterministic development evaluator.

    This is NOT intended to represent real AI evaluation.
    It exists so the complete assessment pipeline can be tested
    before IBM Bob credentials/integration are available.
    """

    def evaluate(
        self,
        questions: list[dict],
        answers: list[dict],
    ) -> EvaluationResult:

        answer_map = {
            answer["question_id"]: answer.get("answer", "").strip()
            for answer in answers
        }

        # Development-only baseline.
        # Every answer starts at 50 and receives a small deterministic
        # adjustment based on whether the developer supplied a meaningful
        # response. This intentionally does NOT perform keyword scoring.
        domain_scores = {
            "APIs": 50,
            "Architecture": 50,
            "Database": 50,
            "Security": 50,
        }

        evidence = {
            "APIs": "Mock evaluation: API reasoning requires IBM Bob evaluation.",
            "Architecture": "Mock evaluation: architecture reasoning requires IBM Bob evaluation.",
            "Database": "Mock evaluation: database reasoning requires IBM Bob evaluation.",
            "Security": "Mock evaluation: security reasoning requires IBM Bob evaluation.",
        }

        for question in questions:
            question_id = question["question_id"]
            domain = question.get("domain")

            if domain not in domain_scores:
                continue

            answer = answer_map.get(question_id, "")

            if answer:
                domain_scores[domain] += 10

        domain_scores = {
            domain: min(100, score)
            for domain, score in domain_scores.items()
        }

        overall_score = round(
            sum(domain_scores.values()) / len(domain_scores)
        )

        next_focus = min(
            domain_scores,
            key=domain_scores.get,
        )

        return EvaluationResult(
            evaluator="mock",
            domain_scores={
                domain: {
                    "score": score,
                    "confidence": "LOW",
                    "evidence": evidence[domain],
                }
                for domain, score in domain_scores.items()
            },
            cross_domain_evidence=[
                "Mock evaluation does not provide semantic cross-domain reasoning."
            ],
            overall_score=overall_score,
            summary=(
                "Development mock evaluation completed. "
                "Scores are placeholders and must not be treated as AI judgment."
            ),
            next_focus=next_focus,
        )


def evaluate_assessment(
    questions: list[dict],
    answers: list[dict],
) -> EvaluationResult:
    return MockEvaluator().evaluate(
        questions=questions,
        answers=answers,
    )