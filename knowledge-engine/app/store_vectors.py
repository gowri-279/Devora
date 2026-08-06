from pymongo import MongoClient
from dotenv import load_dotenv
from app.embeddings import embed_texts
import os

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
DATABASE_NAME = os.getenv("MONGODB_DATABASE", "devora")
COLLECTION_NAME = os.getenv("MONGODB_COLLECTION", "knowledge_chunks")

client = MongoClient(MONGODB_URI)

db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]


def add_chunks(chunks):
    """
    Generate embeddings and store chunks in MongoDB.
    Returns number of inserted records.
    """

    if not chunks:
        return 0

    texts = [c["text"] for c in chunks]
    embeddings = embed_texts(texts)

    records = []

    for chunk, embedding in zip(chunks, embeddings):
        record = {
            **chunk,
            "embedding": embedding
        }
        records.append(record)

    # Clear old data for this project
    project_ids = {
        c.get("project_id")
        for c in chunks
        if c.get("project_id") is not None
    }

    for pid in project_ids:
        collection.delete_many({"project_id": pid})

    result = collection.insert_many(records)

    return len(result.inserted_ids)


if __name__ == "__main__":
    from app.prepare_vectors import records

    project_ids = {
        r.get("project_id")
        for r in records
        if r.get("project_id") is not None
    }

    for pid in project_ids:
        collection.delete_many({"project_id": pid})

    result = collection.insert_many(records)

    total = collection.count_documents({})

    print(f"Inserted {len(result.inserted_ids)} vector records")
    print(f"Total documents in collection: {total}")

    for pid in project_ids:
        count = collection.count_documents({"project_id": pid})
        print(f"Documents for project '{pid}': {count}")