from mcp.server.mcpserver import MCPServer


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
    Search Devora's project knowledge for information
    relevant to a developer's question.
    """

    return f"""
Devora Knowledge Result

Project: {project_id}
Question: {question}

This is a temporary MCP integration test.

Devora's Knowledge Engine will provide the actual project context here.
""".strip()


if __name__ == "__main__":
    server.run(transport="stdio")