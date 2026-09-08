import os

import httpx
from mcp.server.mcpserver import MCPServer


DEVORA_BACKEND_URL = os.getenv(
    "DEVORA_BACKEND_URL",
    "http://127.0.0.1:8000",
)


server = MCPServer(
    name="Devora Knowledge",
    version="1.0.0",
)


@server.tool()
async def search_devora_knowledge(
    question: str,
    project_id: str = "devora",
) -> str:
    """
    Search Devora's Knowledge Engine for project information
    relevant to a developer's question.
    """

    if not question.strip():
        return "Question cannot be empty."

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{DEVORA_BACKEND_URL}/ask-bob",
                json={
                    "question": question,
                    "project_id": project_id,
                },
            )

            response.raise_for_status()
            data = response.json()

    except httpx.HTTPError as exc:
        return f"Knowledge Engine request failed: {exc}"

    contexts = data.get("contexts", [])

    if not contexts:
        return data.get(
            "answer",
            "No relevant project knowledge was found for this question.",
        )

    formatted_contexts = []
    for index, context in enumerate(contexts[:5], start=1):
        formatted_contexts.append(
            f"""
[{index}] {context.get("source_file", "Unknown source")}
Section: {context.get("section_title", "Unknown section")}
Confidence: {context.get("confidence", "unknown")}
Score: {context.get("score", 0)}

{context.get("context", "")}
""".strip()
        )

    return "\n\n".join(formatted_contexts)


if __name__ == "__main__":
    server.run(transport="stdio")