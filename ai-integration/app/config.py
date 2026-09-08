import os

from dotenv import load_dotenv


load_dotenv()


# IBM Bob / Bob Shell configuration
BOB_API_KEY = os.getenv("BOB_API_KEY")

# Backward-compatible name used by existing DEVORA code.
IBM_BOB_API_KEY = os.getenv("IBM_BOB_API_KEY") or BOB_API_KEY

IBM_BOB_ENDPOINT = os.getenv("IBM_BOB_ENDPOINT")

DEVORA_BOB_MODE = os.getenv(
    "DEVORA_BOB_MODE",
    "mock",
)