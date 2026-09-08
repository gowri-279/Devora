from dotenv import load_dotenv

from app.embeddings import embed_texts
from app.db import get_chunks_collection

load_dotenv()

collection = get_chunks_collection()

INSERT_BATCH_SIZE = 500


def add_chunks(chunks):
    """
    Generate embeddings and store chunks in MongoDB.

    Clears old chunks before inserting new ones, keyed by
    (project_id, source_file) for project-scope chunks OR
    (project_id=None, source_file) for team-scope chunks.

    MongoDB inserts are performed in smaller batches so that large
    repository ingestions do not require one enormous insert_many()
    operation.

    Returns number of inserted records.
    """

    if not chunks:
        return 0

    texts = [c["text"] for c in chunks]
    embeddings = embed_texts(texts)

    records = []

    for chunk, embedding in zip(
        chunks,
        embeddings,
    ):
        records.append(
            {
                **chunk,
                "embedding": embedding,
            }
        )

    # Clear old chunks for every (project_id, source_file) combo
    # present in this batch. This covers BOTH project-scope docs
    # and team-scope docs.
    seen_keys = set()

    for c in chunks:
        key = (
            c.get("project_id"),
            c["source_file"],
        )

        if key in seen_keys:
            continue

        seen_keys.add(key)

        collection.delete_many(
            {
                "project_id": key[0],
                "source_file": key[1],
            }
        )

    # Insert in smaller batches instead of one enormous
    # insert_many() operation.
    inserted_count = 0

    for start in range(
        0,
        len(records),
        INSERT_BATCH_SIZE,
    ):
        batch = records[
            start:start + INSERT_BATCH_SIZE
        ]

        result = collection.insert_many(
            batch
        )

        inserted_count += len(
            result.inserted_ids
        )

        print(
            ">>> VECTOR INSERT BATCH:",
            f"{start + len(batch)}/{len(records)}"
        )

    return inserted_count


if __name__ == "__main__":
    # Debug/manual run: re-inserts whatever prepare_vectors.py
    # last built.
    from app.prepare_vectors import records

    inserted = add_chunks(records)

    total = collection.count_documents({})

    print(
        f"Inserted {inserted} vector records"
    )

    print(
        f"Total documents in collection: {total}"
    )