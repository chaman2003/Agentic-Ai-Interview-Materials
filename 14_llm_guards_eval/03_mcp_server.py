# ============================================================
# MCP (MODEL CONTEXT PROTOCOL) — Server Implementation
# ============================================================
# MCP = standardized protocol for giving LLMs access to tools and data
# Think of it as USB-C for AI tools — one standard, any LLM can plug in
#
# pip install mcp
# Official docs: https://modelcontextprotocol.io

"""
HOW MCP WORKS:

┌─────────────┐     MCP Protocol      ┌─────────────┐
│  LLM Client │ ◄──────────────────► │  MCP Server │
│ (Claude,    │    JSON-RPC over       │  (Your app) │
│  Cursor)    │   stdio/HTTP/SSE       │             │
└─────────────┘                       └─────────────┘

MCP Server exposes:
  - TOOLS:     functions the LLM can call (like @tool in LangChain)
  - RESOURCES: data the LLM can read (files, DB records)
  - PROMPTS:   pre-defined prompt templates

Key difference from LangChain tools:
  - LangChain tools: tightly coupled to LangChain ecosystem
  - MCP tools: work with ANY MCP-compatible client (Claude, Cursor, any LLM)
"""

# ── BASIC MCP SERVER ─────────────────────────────────────────
import json
from typing import Any

# Using the mcp library (FastMCP for simple servers)
# pip install mcp[cli]

"""
from mcp.server.fastmcp import FastMCP

# Create the MCP server
mcp = FastMCP("Case Management")

# ── DEFINE TOOLS ───────────────────────────────────────────
# Tools = functions the LLM can call
# The docstring IS the description — write it clearly!

@mcp.tool()
def search_cases(
    query: str,
    status: str = "all",
    limit: int = 10
) -> str:
    '''Search for legal cases by keyword.

    Args:
        query: Search keyword to find in case titles and descriptions
        status: Filter by status: "open", "closed", "in_progress", or "all"
        limit: Maximum number of results to return (1-50)

    Returns:
        JSON string with matching cases
    '''
    # In production: query your database
    mock_cases = [
        {"id": "CASE-001", "title": "Smith vs Jones", "status": "open", "amount": 50000},
        {"id": "CASE-002", "title": "Corp vs LLC",    "status": "closed", "amount": 120000},
    ]
    if status != "all":
        mock_cases = [c for c in mock_cases if c["status"] == status]
    matching  = [c for c in mock_cases if query.lower() in c["title"].lower()]
    return json.dumps(matching[:limit], indent=2)


@mcp.tool()
def get_case_details(case_id: str) -> str:
    '''Get complete details for a specific case by its ID.

    Args:
        case_id: The unique case identifier (format: CASE-XXX)

    Returns:
        JSON string with full case details including parties, timeline, documents
    '''
    # Simulate DB lookup
    case = {
        "id":           case_id,
        "title":        "Smith vs Jones",
        "status":       "open",
        "amount":       50000,
        "party_a":      "John Smith",
        "party_b":      "Alice Jones",
        "mediator":     "Advocate Sharma",
        "created_at":   "2024-01-15",
        "next_hearing": "2024-03-20",
        "documents":    ["contract.pdf", "evidence.pdf"]
    }
    return json.dumps(case, indent=2)


@mcp.tool()
def update_case_status(case_id: str, new_status: str, reason: str) -> str:
    '''Update the status of a case.

    Args:
        case_id: The case identifier
        new_status: New status: "open", "in_progress", "resolved", "closed"
        reason: Reason for the status change (for audit log)

    Returns:
        Confirmation message with updated case info
    '''
    valid_statuses = {"open", "in_progress", "resolved", "closed"}
    if new_status not in valid_statuses:
        return json.dumps({"error": f"Invalid status. Must be one of: {valid_statuses}"})

    # In production: update DB
    return json.dumps({
        "success":    True,
        "case_id":    case_id,
        "new_status": new_status,
        "reason":     reason,
        "updated_at": "2024-03-15T10:30:00Z"
    })


# ── DEFINE RESOURCES ─────────────────────────────────────────
# Resources = data the LLM can read (like files, DB records)
# Different from tools — resources are READ-ONLY data, tools are ACTIONS

@mcp.resource("cases://active")
def get_active_cases() -> str:
    '''All currently active cases in the system'''
    return json.dumps([
        {"id": "CASE-001", "status": "open"},
        {"id": "CASE-042", "status": "in_progress"},
    ])

@mcp.resource("case://{case_id}")
def get_case_resource(case_id: str) -> str:
    '''Individual case data - read-only access'''
    return json.dumps({"id": case_id, "title": "Case details here..."})


# ── DEFINE PROMPTS ───────────────────────────────────────────
# Prompts = reusable prompt templates exposed through MCP

@mcp.prompt()
def case_summary_prompt(case_id: str) -> str:
    '''Generate a professional summary for a case'''
    return f'Please retrieve the details for {case_id} and write a 3-sentence professional summary suitable for a client email.'


# ── RUN THE SERVER ────────────────────────────────────────────
if __name__ == "__main__":
    mcp.run()
    # Run as stdio server: python 03_mcp_server.py
    # Or: mcp dev 03_mcp_server.py  (with inspector UI)
"""

# ── MCP CONCEPTS FOR INTERVIEW ────────────────────────────────
MCP_CONCEPTS = """
KEY MCP INTERVIEW POINTS:

1. WHAT IS MCP?
   Model Context Protocol — a standardized open protocol by Anthropic that
   defines how LLMs connect to external tools and data sources.
   "USB-C for AI" — one standard, works with any compatible client.

2. MCP COMPONENTS:
   - Tools:     Functions the LLM can call (read/write actions)
   - Resources: Data the LLM can read (files, DB records, APIs)
   - Prompts:   Pre-built prompt templates

3. MCP vs LANGCHAIN TOOLS:
   LangChain tools: Python-only, tied to LangChain ecosystem
   MCP tools:       Language-agnostic, any MCP client can use them
                    Claude desktop, Cursor, Continue.dev all support MCP natively

4. TRANSPORT PROTOCOLS:
   - stdio:   Server runs as a subprocess, communicates via stdin/stdout
   - HTTP/SSE: Server runs as a web service (for remote servers)

5. WHY USE MCP?
   - Build tools once, use from Claude, Cursor, any LLM client
   - Standard schema for tool descriptions → better LLM comprehension
   - Separation of concerns: tools live in their own server
   - You built MCP integrations at Cortex Craft AI
"""

print(MCP_CONCEPTS)
