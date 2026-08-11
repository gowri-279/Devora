from pymongo import MongoClient
from dotenv import load_dotenv
from app.embeddings import embed_texts
from app.db import get_chunks_collection
import os

load_dotenv()

collection = get_chunks_collection()


def add_chunks(chunks):
    """
    Generate embeddings and store chunks in MongoDB.

    Clears old chunks before inserting new ones, keyed by (project_id,
    source_file) for project-scope chunks OR (project_id=None,
    source_file) for team-scope chunks. This is the fix for the bug where
    team-scope chunks (project_id=None) never got cleared on re-ingest —
    the old version only deleted by non-None project_ids, so re-uploading
    team_foundations.md just kept piling up duplicate old+new copies
    forever instead of replacing them.

    Returns number of inserted records.
    """

    if not chunks:
        return 0

    texts = [c["text"] for c in chunks]
    embeddings = embed_texts(texts)

    records = []
    for chunk, embedding in zip(chunks, embeddings):
        records.append({**chunk, "embedding": embedding})

    # Clear old chunks for every (project_id, source_file) combo present
    # in this batch — covers BOTH project-scope docs (project_id set) AND
    # team-scope docs (project_id=None), unlike the old version.
    seen_keys = set()
    for c in chunks:
        key = (c.get("project_id"), c["source_file"])
        if key in seen_keys:
            continue
        seen_keys.add(key)
        collection.delete_many({"project_id": key[0], "source_file": key[1]})

    result = collection.insert_many(records)

    return len(result.inserted_ids)


if __name__ == "__main__":
    # Debug/manual run: re-inserts whatever prepare_vectors.py last built.
    from app.prepare_vectors import records

    inserted = add_chunks(records)  # goes through the same fixed dedupe logic above

    total = collection.count_documents({})
    print(f"Inserted {inserted} vector records")
    print(f"Total documents in collection: {total}")
