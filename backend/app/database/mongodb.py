import os

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
DATABASE_NAME = os.getenv("MONGODB_DATABASE", "devora")

_client = None


def get_client() -> MongoClient:
    global _client

    if _client is None:
        if not MONGODB_URI:
            raise RuntimeError(
                "MONGODB_URI is not set — check the root .env file."
            )

        _client = MongoClient(MONGODB_URI)

    return _client


def get_db():
    return get_client()[DATABASE_NAME]


def get_users_collection():
    return get_db()["users"]


def get_teams_collection():
    return get_db()["teams"]


def get_assessments_collection():
    return get_db()["assessments"]


def get_assessment_results_collection():
    return get_db()["assessment_results"]


def get_projects_collection():
    return get_db()["projects"]


def check_connection() -> bool:
    get_client().admin.command("ping")
    return True