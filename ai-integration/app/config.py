import os

from dotenv import load_dotenv

load_dotenv()


IBM_BOB_API_KEY = os.getenv("IBM_BOB_API_KEY")
IBM_BOB_ENDPOINT = os.getenv("IBM_BOB_ENDPOINT")
DEVORA_BOB_MODE = os.getenv("DEVORA_BOB_MODE", "mock")