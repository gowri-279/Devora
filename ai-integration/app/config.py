import os
from dotenv import load_dotenv

load_dotenv()

BOB_API_KEY = os.getenv("BOB_API_KEY")

print("Bob API key configured:", bool(BOB_API_KEY))