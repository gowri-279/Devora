"""
Single place that owns the MongoDB client and collection handles.

Everything else (search.py, store_vectors.py, main.py, projects.py,
raw_storage.py) should import from here instead of each opening its own
MongoClient — that duplication is what let the team-doc-duplication bug
slip in (store_vectors.py's old delete logic didn't match what
connect.py/search.py assumed). One connection module = one place to get
collection names right.
"""

import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
DATABASE_NAME = os.getenv("MONGODB_DATABASE", "devora")
CHUNKS_COLLECTION_NAME = os.getenv("MONGODB_COLLECTION", "knowledge_chunks")

# New collections for items 1 & 2 (multi-project archiving + raw storage).
RAW_DOCUMENTS_COLLECTION_NAME = "raw_documents"
PROJECTS_COLLECTION_NAME = "projects_meta"
GAPS_COLLECTION_NAME = "knowledge_gaps"

_client = None


def get_client() -> MongoClient:
    global _client
    if _client is None:
        if not MONGODB_URI:
            raise RuntimeError("MONGODB_URI is not set — check your .env file.")
        _client = MongoClient(MONGODB_URI)
    return _client


def get_db():
    return get_client()[DATABASE_NAME]


def get_chunks_collection():
    return get_db()[CHUNKS_COLLECTION_NAME]


def get_raw_documents_collection():
    return get_db()[RAW_DOCUMENTS_COLLECTION_NAME]


def get_projects_collection():
    return get_db()[PROJECTS_COLLECTION_NAME]


def get_gaps_collection():
    return get_db()[GAPS_COLLECTION_NAME]


def check_connection() -> bool:
    get_client().admin.command("ping")
    return True
