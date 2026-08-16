from app.config import (
    DEVORA_BOB_MODE,
    IBM_BOB_API_KEY,
    IBM_BOB_ENDPOINT,
)


class IBMBobClient:
    """
    Client responsible for communicating with IBM Bob.
    """

    def __init__(
        self,
        api_key: str | None = IBM_BOB_API_KEY,
        endpoint: str | None = IBM_BOB_ENDPOINT,
    ):
        self.api_key = api_key
        self.endpoint = endpoint

    def generate(self, prompt: str) -> str:
        if DEVORA_BOB_MODE == "mock":
            return self._mock_generate(prompt)

        return self._live_generate(prompt)

    def _mock_generate(self, prompt: str) -> str:
        return (
            "Mock Bob response: I generated this answer using "
            "the grounded project context provided by Devora."
        )

    def _live_generate(self, prompt: str) -> str:
        if not self.api_key:
            raise RuntimeError("IBM_BOB_API_KEY is not configured.")

        if not self.endpoint:
            raise RuntimeError("IBM_BOB_ENDPOINT is not configured.")

        raise NotImplementedError(
            "Live IBM Bob integration is not configured yet."
        )