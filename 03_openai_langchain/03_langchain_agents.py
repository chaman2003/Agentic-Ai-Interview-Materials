# ============================================================
# LANGCHAIN AGENTS + TOOLS — Interview Essentials
# ============================================================
# pip install langchain langchain-openai

import os
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.tools import tool
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder

llm = ChatOpenAI(model="gpt-4", temperature=0)

# ── WHAT IS AN AGENT? ─────────────────────────────────────────
# An agent is an LLM that can use TOOLS to accomplish tasks.
# It follows this loop:
#   Reason → Decide which tool to use (if any) → Call tool → Observe result → Repeat
# Until it has enough information to give a final answer.

# Vs Chain: A chain has a FIXED sequence of steps.
#           An agent DYNAMICALLY decides what to do next.


# ── TOOLS ────────────────────────────────────────────────────
# A tool is a Python function the agent can call.
# @tool decorator reads the docstring as the tool description — write it clearly!

@tool
def search_legal_cases(query: str) -> str:
    """Search for legal cases by keyword. Returns a list of matching case summaries."""
    # In real app: query database or search engine
    mock_results = [
        {"case_id": "CASE001", "title": "Smith vs Jones", "status": "Open", "type": "Contract dispute"},
        {"case_id": "CASE002", "title": "Corp vs LLC",    "status": "Closed", "type": "IP infringement"},
    ]
    matching = [c for c in mock_results if query.lower() in c["title"].lower()]
    return str(matching) if matching else "No cases found."


@tool
def get_case_details(case_id: str) -> str:
    """Retrieve full details of a specific case by its ID."""
    mock_cases = {
        "CASE001": {
            "id": "CASE001",
            "title": "Smith vs Jones",
            "status": "Open",
            "amount": 50000,
            "mediator": "Advocate Sharma",
            "next_hearing": "2024-03-20"
        }
    }
    case = mock_cases.get(case_id.upper())
    return str(case) if case else f"Case {case_id} not found."


@tool
def calculate_settlement(case_id: str, discount_percent: float) -> str:
    """Calculate a discounted settlement amount for a case."""
    # Simulate looking up the case amount
    original = 50000
    settlement = original * (1 - discount_percent / 100)
    return f"Settlement for {case_id}: ₹{settlement:,.0f} (after {discount_percent}% discount)"


# ── BUILD THE AGENT ───────────────────────────────────────────
tools = [search_legal_cases, get_case_details, calculate_settlement]

# System prompt tells agent who it is and what it can do
prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a legal case management assistant.
    You help users find and analyze dispute cases.
    Use the available tools to answer questions accurately."""),
    MessagesPlaceholder("chat_history", optional=True),
    ("human", "{input}"),
    MessagesPlaceholder("agent_scratchpad")   # agent's internal reasoning
])

# Create agent
agent = create_openai_tools_agent(llm, tools, prompt)

# AgentExecutor runs the Reason → Act → Observe loop
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,    # prints each step — great for debugging
    max_iterations=5  # safety limit to prevent infinite loops
)


def run_agent(question):
    """Run the agent and return its answer"""
    result = agent_executor.invoke({"input": question})
    return result["output"]


# Examples:
# run_agent("Find cases about contract disputes")
# run_agent("Get full details for case CASE001")
# run_agent("Calculate settlement for CASE001 with 20% discount")
# run_agent("Search for Smith cases and tell me the settlement with 15% discount")


# ── AGENT WITH MEMORY ─────────────────────────────────────────
from langchain.memory import ConversationBufferMemory

memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True
)

agent_with_memory = AgentExecutor(
    agent=agent,
    tools=tools,
    memory=memory,
    verbose=True
)

# Now agent remembers previous messages in the conversation
# run_agent_with_memory("Find CASE001")
# run_agent_with_memory("What's the settlement with 10% discount?")  # remembers CASE001


# ── INTERVIEW SUMMARY ────────────────────────────────────────
"""
Q: What is a LangChain agent?
A: An LLM that can use tools to accomplish tasks. It follows the
   Reason → Act → Observe loop until it can answer the user.
   Unlike chains (fixed steps), agents decide dynamically what to do.

Q: What is a tool?
A: A Python function the agent can call. Decorated with @tool.
   The docstring is the description the LLM reads to decide when to use it.

Q: What is AgentExecutor?
A: Runs the agent loop. It calls the agent, executes tool calls,
   feeds results back to the agent, and repeats until done.

Q: What is max_iterations?
A: Safety limit to prevent the agent from looping forever.

Q: How is an agent different from a chain?
A: Chain = fixed sequence (step 1 → step 2 → step 3, always)
   Agent = dynamic (LLM decides: call tool A? call tool B? done?)
"""
