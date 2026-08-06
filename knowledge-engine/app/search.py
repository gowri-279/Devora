from pymongo import MongoClient
from dotenv import load_dotenv
from app.embeddings import embed_query
import os

load_dotenv()

client = MongoClient(os.getenv("MONGODB_URI"))

db = client[os.getenv("MONGODB_DATABASE")]
collection = db[os.getenv("MONGODB_COLLECTION")]

INDEX_NAME = "vector_index"


def reconstruct_section(source_file: str, section_id: str):
    """
    Reconstruct all chunks belonging to the same semantic section
    and remove repeated overlapping paragraphs.
    """

    docs = list(collection.find(
        {
            "source_file": source_file,
            "metadata.section_id": section_id
        },
        {
            "_id": 0,
            "text": 1,
            "metadata.chunk_index": 1
        }
    ).sort("metadata.chunk_index", 1))

    seen = set()
    cleaned_parts = []

    for d in docs:
        # Split by blank lines to compare logical paragraphs
        paragraphs = [p.strip() for p in d["text"].split("\n\n") if p.strip()]

        unique_paragraphs = []

        for p in paragraphs:
            if p not in seen:
                seen.add(p)
                unique_paragraphs.append(p)

        if unique_paragraphs:
            cleaned_parts.append("\n\n".join(unique_paragraphs))

    return "\n\n".join(cleaned_parts)


def search(query: str, project_id: str = "refund-service", top_k: int = 5):
    query_vector = embed_query(query)

    pipeline = [
        {
            "$vectorSearch": {
                "index": INDEX_NAME,
                "path": "embedding",
                "queryVector": query_vector,
                "numCandidates": 50,
                "limit": top_k,
                "filter": {
                    "$or": [
                        {"project_id": project_id},
                        {
                            "$and": [
                                {"scope": "team"},
                                {"project_id": None}
                            ]
                        }
                    ]
                }
            }
        },
        {
            "$project": {
                "_id": 0,
                "chunk_id": 1,
                "source_file": 1,
                "text": 1,
                "scope": 1,
                "metadata": 1,
                "score": {"$meta": "vectorSearchScore"}
            }
        }
    ]

    results = list(collection.aggregate(pipeline))

    final_results = []
    seen = set()

    for r in results:
        section_id = r["metadata"].get("section_id")

        if section_id:
            context = reconstruct_section(r["source_file"], section_id)
        else:
            context = r["text"]

        key = (r["source_file"], context)
        if key in seen:
            continue

        seen.add(key)

        final_results.append({
            "source_file": r["source_file"],
            "scope": r["scope"],
            "score": r["score"],
            "section_title": r["metadata"].get("section_title", ""),
            "context": context
        })

    return final_results


if __name__ == "__main__":
    query = "How do I run the project locally?"

    results = search(query)

    print(f"Query: {query}\n")

    for i, r in enumerate(results, 1):
        print(f"Result {i} | score={r['score']:.4f}")
        print(f"Source: {r['source_file']} ({r['scope']})")
        print(f"Section: {r['section_title']}\n")

        print(r["context"].strip())

        print("\n" + "-" * 80 + "\n")