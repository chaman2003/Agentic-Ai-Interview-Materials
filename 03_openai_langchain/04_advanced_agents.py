"""
04_advanced_agents.py — Advanced LangChain Agent Patterns
==========================================================
Covers:
  - ReAct agent pattern from scratch
  - Tool-calling agent with multiple tools
  - Multi-agent system with LangGraph
  - Agent with structured output (Pydantic)
  - Streaming agent responses
  - Agent with persistent memory (Redis/MongoDB)
  - Error recovery and retries
  - Human-in-the-loop pattern
"""

import os
import json
import asyncio
from typing import Annotated, Sequence, TypedDict, Literal
from datetime import datetime

from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
from langchain_core.output_parsers import StrOutputParser
from langchain.agents import AgentExecutor, create_tool_calling_agent, create_react_agent
from langchain_core.runnables import RunnablePassthrough
from pydantic import BaseModel, Field

# ─────────────────────────────────────────────────────────────────────────────
## 1. REACT AGENT PATTERN FROM SCRATCH
# ─────────────────────────────────────────────────────────────────────────────
# ReAct = Reasoning + Acting. The loop:
#   Thought → Action → Observation → Thought → ... → Final Answer
# We implement the loop manually (no AgentExecutor) for full visibility.

class ReactAgent:
    """
    Minimal ReAct agent implemented from scratch.
    The LLM writes structured text: Thought / Action / Action Input.
    We parse it, run the tool, inject the Observation, and loop.
    """

    SYSTEM_PROMPT = """You are a helpful assistant that solves problems step by step.
You have access to these tools:
{tool_descriptions}

Use this EXACT format on every turn:

Thought: <your reasoning about what to do next>
Action: <tool name, exactly as listed>
Action Input: <JSON arguments for the tool>

When you have the final answer, use:
Thought: I now know the answer.
Final Answer: <your answer>"""

    def __init__(self, tools: list, model: str = "gpt-4o-mini", max_iterations: int = 10):
        self.tools = {t.name: t for t in tools}
        self.llm = ChatOpenAI(model=model, temperature=0)
        self.max_iterations = max_iterations

    def _build_tool_descriptions(self) -> str:
        lines = []
        for name, t in self.tools.items():
            lines.append(f"- {name}: {t.description}")
        return "\n".join(lines)

    def run(self, question: str) -> str:
        system = self.SYSTEM_PROMPT.format(
            tool_descriptions=self._build_tool_descriptions()
        )
        messages = [
            SystemMessage(content=system),
            HumanMessage(content=question)
        ]

        for i in range(self.max_iterations):
            response = self.llm.invoke(messages)
            text = response.content
            print(f"\n[Iteration {i+1}]\n{text}")

            # Check for final answer
            if "Final Answer:" in text:
                return text.split("Final Answer:")[-1].strip()

            # Parse Action and Action Input
            try:
                action_line = [l for l in text.split("\n") if l.startswith("Action:")][0]
                input_line  = [l for l in text.split("\n") if l.startswith("Action Input:")][0]
                action_name  = action_line.replace("Action:", "").strip()
                action_input = input_line.replace("Action Input:", "").strip()
                args = json.loads(action_input)
            except (IndexError, json.JSONDecodeError) as e:
                observation = f"Parsing error: {e}. Please follow the exact format."
            else:
                if action_name not in self.tools:
                    observation = f"Unknown tool '{action_name}'. Available: {list(self.tools.keys())}"
                else:
                    try:
                        observation = str(self.tools[action_name].invoke(args))
                    except Exception as e:
                        observation = f"Tool error: {e}"

            # Append assistant message + observation
            messages.append(AIMessage(content=text))
            messages.append(HumanMessage(content=f"Observation: {observation}"))

        return "Max iterations reached without a final answer."


# ─────────────────────────────────────────────────────────────────────────────
## 2. TOOL-CALLING AGENT WITH MULTIPLE TOOLS
# ─────────────────────────────────────────────────────────────────────────────

# --- Tool definitions ---

@tool
def search_web(query: str) -> str:
    """Search the web for real-time information. Use for current events, news, prices."""
    # In production: integrate with SerpAPI, Tavily, or Bing Search API
    # Mocked here for demonstration
    mock_results = {
        "python news": "Python 3.13 released with JIT compiler. Major performance improvements.",
        "bitcoin price": "Bitcoin is trading at $67,000 as of today.",
        "openai news": "OpenAI released o3 model with improved reasoning capabilities.",
    }
    query_lower = query.lower()
    for key, val in mock_results.items():
        if key in query_lower:
            return val
    return f"Web search results for '{query}': Found 10 results. Top result: General information about {query}."


@tool
def calculate(expression: str) -> str:
    """
    Evaluate a mathematical expression. Use for arithmetic, percentages, conversions.
    Input must be a valid Python math expression string.
    Example: '(100 * 0.15) + 50' or 'math.sqrt(144)'
    """
    import math
    try:
        # Safe eval with only math functions
        allowed = {k: v for k, v in math.__dict__.items() if not k.startswith("_")}
        allowed["abs"] = abs
        result = eval(expression, {"__builtins__": {}}, allowed)
        return f"Result: {result}"
    except Exception as e:
        return f"Calculation error: {e}. Check the expression syntax."


class DatabaseQueryInput(BaseModel):
    table: str = Field(description="Table name to query (users, products, orders)")
    filter_by: str = Field(default="", description="Optional: field=value filter condition")
    limit: int = Field(default=5, ge=1, le=100, description="Max rows to return")

@tool("query_database", args_schema=DatabaseQueryInput)
def query_database(table: str, filter_by: str = "", limit: int = 5) -> str:
    """
    Query the application database for structured data.
    Use for looking up users, products, orders, or statistics.
    """
    # Mock database
    mock_data = {
        "users": [
            {"id": 1, "name": "Alice", "email": "alice@example.com", "plan": "pro"},
            {"id": 2, "name": "Bob", "email": "bob@example.com", "plan": "free"},
        ],
        "products": [
            {"id": 1, "name": "Widget Pro", "price": 49.99, "stock": 150},
            {"id": 2, "name": "Gadget X", "price": 29.99, "stock": 0},
        ],
        "orders": [
            {"id": 101, "user_id": 1, "total": 149.97, "status": "shipped"},
            {"id": 102, "user_id": 2, "total": 29.99, "status": "pending"},
        ]
    }
    if table not in mock_data:
        return f"Table '{table}' not found. Available tables: {list(mock_data.keys())}"

    rows = mock_data[table]
    if filter_by:
        key, _, val = filter_by.partition("=")
        rows = [r for r in rows if str(r.get(key.strip(), "")) == val.strip()]

    return json.dumps(rows[:limit], indent=2)


def run_multi_tool_agent():
    """Demonstrate a tool-calling agent with web, calculator, and DB tools."""
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    tools = [search_web, calculate, query_database]

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful business assistant. Use the provided tools to answer questions accurately."),
        MessagesPlaceholder("chat_history", optional=True),
        ("human", "{input}"),
        MessagesPlaceholder("agent_scratchpad"),
    ])

    agent = create_tool_calling_agent(llm, tools, prompt)
    executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        max_iterations=5,
        handle_parsing_errors=True,
        return_intermediate_steps=True,  # for debugging
    )

    questions = [
        "What's 15% of 340, and also look up how many Widget Pro units we have in stock.",
        "Find all orders with status=shipped and calculate the average order total.",
    ]

    for q in questions:
        print(f"\n{'='*60}\nQuestion: {q}\n{'='*60}")
        result = executor.invoke({"input": q, "chat_history": []})
        print(f"\nFinal Answer: {result['output']}")

        # Inspect intermediate steps
        for step in result.get("intermediate_steps", []):
            action, observation = step
            print(f"  Tool: {action.tool} | Args: {action.tool_input}")


# ─────────────────────────────────────────────────────────────────────────────
## 3. MULTI-AGENT SYSTEM WITH LANGGRAPH
# ─────────────────────────────────────────────────────────────────────────────

try:
    from langgraph.graph import StateGraph, END
    from langgraph.prebuilt import ToolNode
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    print("Note: langgraph not installed. Run: pip install langgraph")


class AgentState(TypedDict):
    """State shared between all nodes in the multi-agent graph."""
    messages: Annotated[Sequence[BaseMessage], lambda x, y: x + y]
    next: str
    task_type: str  # "research", "calculation", "database"


def build_multi_agent_graph():
    """
    Build a supervisor + specialized agents graph.

    Architecture:
      supervisor → routes to → researcher / calculator / db_agent
      each specialized agent → reports back to → supervisor
      supervisor → END when done
    """
    if not LANGGRAPH_AVAILABLE:
        print("LangGraph not available. Skipping multi-agent demo.")
        return None

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    # --- Specialized agent nodes ---

    def research_agent(state: AgentState) -> dict:
        """Handles web search tasks."""
        messages = state["messages"]
        response = llm.bind_tools([search_web]).invoke(messages)
        return {"messages": [response]}

    def calculation_agent(state: AgentState) -> dict:
        """Handles mathematical computation tasks."""
        messages = state["messages"]
        response = llm.bind_tools([calculate]).invoke(messages)
        return {"messages": [response]}

    def database_agent(state: AgentState) -> dict:
        """Handles database query tasks."""
        messages = state["messages"]
        response = llm.bind_tools([query_database]).invoke(messages)
        return {"messages": [response]}

    def supervisor(state: AgentState) -> dict:
        """
        Supervisor decides which agent to call next or if done.
        Returns routing decision in 'next' field.
        """
        route_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a supervisor routing tasks to specialized agents.
Available agents:
- researcher: for web search and real-time information
- calculator: for math and numerical computations
- database: for querying structured data
- FINISH: when the task is complete

Based on the conversation, decide the next step."""),
            MessagesPlaceholder("messages"),
            ("human", "What should be done next? Reply with ONLY one word: researcher, calculator, database, or FINISH")
        ])

        chain = route_prompt | llm | StrOutputParser()
        decision = chain.invoke({"messages": state["messages"]}).strip().lower()

        valid = {"researcher", "calculator", "database", "finish"}
        if decision not in valid:
            decision = "finish"

        return {"next": decision}

    def router(state: AgentState) -> Literal["researcher", "calculator", "database", "__end__"]:
        """Edge function that reads the supervisor's routing decision."""
        if state["next"] == "finish":
            return END
        return state["next"]

    # --- Build the graph ---
    graph = StateGraph(AgentState)

    graph.add_node("supervisor", supervisor)
    graph.add_node("researcher", research_agent)
    graph.add_node("calculator", calculation_agent)
    graph.add_node("database", database_agent)

    # Tool execution nodes
    graph.add_node("research_tools", ToolNode([search_web]))
    graph.add_node("calc_tools", ToolNode([calculate]))
    graph.add_node("db_tools", ToolNode([query_database]))

    # Edges
    graph.set_entry_point("supervisor")
    graph.add_conditional_edges("supervisor", router)

    # Each agent → its tools → back to supervisor
    graph.add_edge("researcher", "research_tools")
    graph.add_edge("calculator", "calc_tools")
    graph.add_edge("database", "db_tools")
    graph.add_edge("research_tools", "supervisor")
    graph.add_edge("calc_tools", "supervisor")
    graph.add_edge("db_tools", "supervisor")

    return graph.compile()


def run_multi_agent(question: str):
    app = build_multi_agent_graph()
    if not app:
        return

    initial_state = {
        "messages": [HumanMessage(content=question)],
        "next": "",
        "task_type": ""
    }

    for step in app.stream(initial_state, {"recursion_limit": 20}):
        for node_name, node_output in step.items():
            if "messages" in node_output:
                last_msg = node_output["messages"][-1]
                print(f"[{node_name}]: {getattr(last_msg, 'content', '')[:200]}")


# ─────────────────────────────────────────────────────────────────────────────
## 4. AGENT WITH STRUCTURED OUTPUT (PYDANTIC)
# ─────────────────────────────────────────────────────────────────────────────

class ResearchReport(BaseModel):
    """Structured output model for a research report."""
    topic: str = Field(description="The main topic researched")
    summary: str = Field(description="2-3 sentence summary of findings")
    key_facts: list[str] = Field(description="3-5 key facts discovered", min_length=1)
    sources_used: list[str] = Field(description="Tools/sources consulted")
    confidence: Literal["high", "medium", "low"] = Field(
        description="Confidence level in the findings"
    )
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


def run_structured_output_agent(topic: str) -> ResearchReport:
    """Agent that returns a validated Pydantic report instead of raw text."""
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    # Bind tools for data gathering
    tools = [search_web, query_database]
    agent_llm = llm.bind_tools(tools)

    messages = [
        SystemMessage(content=f"""Research the topic and gather information using available tools.
After gathering sufficient information, provide a structured report."""),
        HumanMessage(content=f"Research topic: {topic}")
    ]

    # Tool execution loop (simplified)
    for _ in range(5):
        response = agent_llm.invoke(messages)
        messages.append(response)

        if not response.tool_calls:
            break  # No more tools to call

        for tc in response.tool_calls:
            tool_map = {t.name: t for t in tools}
            if tc["name"] in tool_map:
                result = tool_map[tc["name"]].invoke(tc["args"])
                messages.append(ToolMessage(content=str(result), tool_call_id=tc["id"]))

    # Now extract structured output
    structured_llm = llm.with_structured_output(ResearchReport)
    messages.append(HumanMessage(
        content="Based on your research above, generate the structured ResearchReport."
    ))
    report = structured_llm.invoke(messages)
    return report


# ─────────────────────────────────────────────────────────────────────────────
## 5. STREAMING AGENT RESPONSES
# ─────────────────────────────────────────────────────────────────────────────

async def stream_agent_response(question: str):
    """
    Stream agent responses token by token.
    Handles both text tokens and tool call events.
    """
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, streaming=True)
    tools = [search_web, calculate]
    agent_llm = llm.bind_tools(tools)

    messages = [HumanMessage(content=question)]
    tool_map = {t.name: t for t in tools}

    print(f"\nStreaming response for: {question}")
    print("-" * 40)

    for iteration in range(5):
        current_text = ""
        tool_calls = []

        # Stream the response
        async for chunk in agent_llm.astream(messages):
            # Stream text content
            if chunk.content:
                print(chunk.content, end="", flush=True)
                current_text += chunk.content

            # Accumulate tool calls (they come in chunks too)
            if hasattr(chunk, "tool_call_chunks") and chunk.tool_call_chunks:
                for tc_chunk in chunk.tool_call_chunks:
                    # Build up tool calls from chunks
                    idx = tc_chunk.get("index", 0)
                    while len(tool_calls) <= idx:
                        tool_calls.append({"id": "", "name": "", "args": ""})
                    if tc_chunk.get("id"):
                        tool_calls[idx]["id"] = tc_chunk["id"]
                    if tc_chunk.get("name"):
                        tool_calls[idx]["name"] = tc_chunk["name"]
                    if tc_chunk.get("args"):
                        tool_calls[idx]["args"] += tc_chunk["args"]

        # If no tool calls, we're done
        if not tool_calls or not any(tc["name"] for tc in tool_calls):
            print("\n" + "-" * 40)
            print("Streaming complete.")
            break

        # Execute tools and continue
        from langchain_core.messages import AIMessage as AI
        messages.append(AI(content=current_text, tool_calls=[
            {"id": tc["id"], "name": tc["name"], "args": json.loads(tc["args"] or "{}")}
            for tc in tool_calls if tc["name"]
        ]))

        for tc in tool_calls:
            if tc["name"] in tool_map:
                args = json.loads(tc["args"] or "{}")
                result = tool_map[tc["name"]].invoke(args)
                print(f"\n[Tool: {tc['name']}] → {str(result)[:100]}")
                messages.append(ToolMessage(content=str(result), tool_call_id=tc["id"]))


def demo_sync_streaming():
    """Synchronous streaming with LCEL chain (simpler pattern)."""
    from langchain_core.output_parsers import StrOutputParser

    llm = ChatOpenAI(model="gpt-4o-mini", streaming=True)
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant. Be thorough but concise."),
        ("human", "{question}")
    ])
    chain = prompt | llm | StrOutputParser()

    print("\nSync streaming demo:")
    for chunk in chain.stream({"question": "Explain how neural networks work in 5 steps"}):
        print(chunk, end="", flush=True)
    print()


# ─────────────────────────────────────────────────────────────────────────────
## 6. AGENT WITH PERSISTENT MEMORY (REDIS / MONGODB)
# ─────────────────────────────────────────────────────────────────────────────

from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory, InMemoryChatMessageHistory

# --- In-Memory store (development) ---
session_store: dict[str, InMemoryChatMessageHistory] = {}

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    """Session history factory — called by RunnableWithMessageHistory."""
    if session_id not in session_store:
        session_store[session_id] = InMemoryChatMessageHistory()
    return session_store[session_id]


def build_memory_agent():
    """Agent with RunnableWithMessageHistory for automatic history management."""
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    tools = [search_web, calculate]

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant with memory. Reference previous conversation when relevant."),
        MessagesPlaceholder("history"),
        ("human", "{input}"),
        MessagesPlaceholder("agent_scratchpad"),
    ])

    agent = create_tool_calling_agent(llm, tools, prompt)
    executor = AgentExecutor(agent=agent, tools=tools, verbose=False)

    # Wrap with history management
    agent_with_history = RunnableWithMessageHistory(
        executor,
        get_session_history,
        input_messages_key="input",
        history_messages_key="history",
    )
    return agent_with_history


# --- Redis-backed history (production) ---
# Requires: pip install redis langchain-redis

def get_redis_history(session_id: str) -> BaseChatMessageHistory:
    """Production: Redis-backed message history with TTL."""
    try:
        from langchain_community.chat_message_histories import RedisChatMessageHistory
        return RedisChatMessageHistory(
            session_id=session_id,
            url=os.getenv("REDIS_URL", "redis://localhost:6379"),
            ttl=86400  # 24 hour TTL
        )
    except ImportError:
        print("Redis not available, falling back to in-memory")
        return get_session_history(session_id)


# --- MongoDB-backed history (production) ---
def get_mongo_history(session_id: str) -> BaseChatMessageHistory:
    """Production: MongoDB-backed message history."""
    try:
        from langchain_mongodb.chat_message_histories import MongoDBChatMessageHistory
        return MongoDBChatMessageHistory(
            connection_string=os.getenv("MONGODB_URI", "mongodb://localhost:27017"),
            session_id=session_id,
            database_name="chatbot_db",
            collection_name="chat_histories",
        )
    except ImportError:
        print("MongoDB client not available, falling back to in-memory")
        return get_session_history(session_id)


def demo_persistent_memory():
    """Demonstrate multi-turn conversation with persistent memory."""
    agent = build_memory_agent()
    session_id = "user_123_session_456"

    config = {"configurable": {"session_id": session_id}}

    conversations = [
        "My name is Alice and I work at a startup called TechVenture.",
        "What's 15% of 8500? That's my quarterly bonus.",
        "What's my name and what company do I work for?",  # Tests memory
    ]

    for message in conversations:
        print(f"\nUser: {message}")
        result = agent.invoke({"input": message}, config=config)
        print(f"Agent: {result['output']}")

    # Show stored history
    history = get_session_history(session_id)
    print(f"\nStored {len(history.messages)} messages in session {session_id}")


# ─────────────────────────────────────────────────────────────────────────────
## 7. ERROR RECOVERY AND RETRIES IN AGENTS
# ─────────────────────────────────────────────────────────────────────────────

import time
from functools import wraps

def with_retry(max_attempts: int = 3, base_delay: float = 1.0, backoff: float = 2.0):
    """Decorator for exponential backoff retry on tool failures."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_error = e
                    if attempt < max_attempts - 1:
                        delay = base_delay * (backoff ** attempt)
                        print(f"  [Retry {attempt+1}/{max_attempts}] Error: {e}. Waiting {delay:.1f}s...")
                        time.sleep(delay)
            raise RuntimeError(f"All {max_attempts} attempts failed. Last error: {last_error}")
        return wrapper
    return decorator


@tool
@with_retry(max_attempts=3)
def flaky_external_api(endpoint: str) -> str:
    """Call an external API that might fail. Retries automatically on failure."""
    import random
    if random.random() < 0.5:  # 50% chance of failure for demo
        raise ConnectionError(f"Connection timeout to {endpoint}")
    return f"Successfully fetched data from {endpoint}: {{'status': 'ok', 'data': [1, 2, 3]}}"


class ResilientAgentExecutor:
    """
    AgentExecutor wrapper with circuit breaker and error recovery.

    Patterns implemented:
    - Retry with exponential backoff
    - Circuit breaker (stop trying after N consecutive failures)
    - Graceful degradation (fallback answers)
    - Error injection into agent context for self-correction
    """

    def __init__(self, agent, tools: list, max_retries: int = 2):
        self.executor = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=8,
        )
        self.max_retries = max_retries
        self.failure_counts: dict[str, int] = {}
        self.circuit_open: dict[str, bool] = {}

    def _is_circuit_open(self, tool_name: str) -> bool:
        return self.circuit_open.get(tool_name, False)

    def _record_failure(self, tool_name: str, threshold: int = 3):
        count = self.failure_counts.get(tool_name, 0) + 1
        self.failure_counts[tool_name] = count
        if count >= threshold:
            self.circuit_open[tool_name] = True
            print(f"  [Circuit Breaker] {tool_name} circuit OPEN after {count} failures")

    def invoke(self, inputs: dict) -> dict:
        last_error = None
        for attempt in range(self.max_retries + 1):
            try:
                result = self.executor.invoke(inputs)
                # Reset failure counts on success
                self.failure_counts.clear()
                self.circuit_open.clear()
                return result
            except Exception as e:
                last_error = e
                print(f"  [Agent Error Attempt {attempt+1}]: {type(e).__name__}: {e}")
                if attempt < self.max_retries:
                    # Modify input to hint at the error
                    inputs = {
                        **inputs,
                        "input": inputs["input"] + f"\n\n[Note: Previous attempt failed with: {e}. Please try a different approach.]"
                    }
                    time.sleep(1.5 ** attempt)

        return {
            "output": f"I encountered an error and couldn't complete the task: {last_error}",
            "error": str(last_error)
        }


# ─────────────────────────────────────────────────────────────────────────────
## 8. HUMAN-IN-THE-LOOP PATTERN
# ─────────────────────────────────────────────────────────────────────────────

class HumanApprovalRequired(Exception):
    """Raised when a tool requires human approval before execution."""
    def __init__(self, tool_name: str, args: dict, reason: str):
        self.tool_name = tool_name
        self.args = args
        self.reason = reason
        super().__init__(f"Human approval required for {tool_name}")


SENSITIVE_TOOLS = {"send_email", "delete_records", "charge_payment", "deploy_code"}


class HumanInTheLoopAgent:
    """
    Agent that pauses and requests human approval for sensitive actions.

    In production: integrate with Slack, email, or a web UI for approvals.
    With LangGraph: use interrupt_before/interrupt_after on sensitive nodes.
    """

    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        self.pending_approvals: list[dict] = []

    @tool
    def send_email(recipient: str, subject: str, body: str) -> str:
        """Send an email to a recipient. REQUIRES human approval."""
        return f"Email sent to {recipient}: '{subject}'"

    @tool
    def delete_records(table: str, condition: str) -> str:
        """Delete database records matching condition. REQUIRES human approval."""
        return f"Deleted records from {table} where {condition}"

    @tool
    def read_database(query: str) -> str:
        """Read-only database query. Safe, no approval needed."""
        return f"Query results: [sample data for: {query}]"

    def _approval_gate(self, tool_name: str, args: dict) -> bool:
        """
        Check if an action needs approval. In production, this would:
        - Create an approval request in the database
        - Send notification to approver (Slack/email)
        - Poll or wait for webhook response
        """
        if tool_name in SENSITIVE_TOOLS:
            print(f"\n{'!'*50}")
            print(f"APPROVAL REQUIRED for: {tool_name}")
            print(f"Arguments: {json.dumps(args, indent=2)}")
            print(f"{'!'*50}")

            # In production: async wait for human response
            # Here: simulate console approval
            response = input("Approve? (yes/no): ").strip().lower()
            return response in ("yes", "y")
        return True

    def run_with_approval(self, question: str) -> str:
        tools = [self.send_email, self.delete_records, self.read_database]
        tool_map = {t.name: t for t in tools}
        agent_llm = self.llm.bind_tools(tools)
        messages = [HumanMessage(content=question)]

        for _ in range(10):
            response = agent_llm.invoke(messages)
            messages.append(response)

            if not response.tool_calls:
                return response.content

            for tc in response.tool_calls:
                name = tc["name"]
                args = tc["args"]

                # Check approval gate
                if not self._approval_gate(name, args):
                    messages.append(ToolMessage(
                        content=f"Action '{name}' was denied by human operator.",
                        tool_call_id=tc["id"]
                    ))
                    continue

                # Execute approved tool
                if name in tool_map:
                    result = tool_map[name].invoke(args)
                    messages.append(ToolMessage(content=str(result), tool_call_id=tc["id"]))

        return "Max iterations reached."


# --- LangGraph Human-in-the-Loop (interrupt pattern) ---
def build_hitl_graph():
    """
    LangGraph human-in-the-loop using interrupt_before.
    The graph pauses before 'sensitive_action' node,
    waits for human input, then resumes.
    """
    if not LANGGRAPH_AVAILABLE:
        print("LangGraph not available.")
        return None

    from langgraph.graph import StateGraph, END
    from langgraph.checkpoint.memory import MemorySaver

    class HitlState(TypedDict):
        messages: Annotated[Sequence[BaseMessage], lambda x, y: x + y]
        approved: bool

    def agent_node(state: HitlState) -> dict:
        llm = ChatOpenAI(model="gpt-4o-mini")
        response = llm.bind_tools([send_email_tool := tool(lambda r,s,b: "sent")(lambda r,s,b: "sent")]).invoke(state["messages"])
        return {"messages": [response]}

    def sensitive_action_node(state: HitlState) -> dict:
        """This node will be interrupted for human review."""
        last_msg = state["messages"][-1]
        print(f"Executing approved sensitive action: {getattr(last_msg, 'content', '')[:100]}")
        return {"messages": [AIMessage(content="Action completed successfully.")]}

    graph = StateGraph(HitlState)
    graph.add_node("agent", agent_node)
    graph.add_node("sensitive_action", sensitive_action_node)
    graph.set_entry_point("agent")
    graph.add_edge("agent", "sensitive_action")
    graph.add_edge("sensitive_action", END)

    # interrupt_before causes the graph to pause BEFORE executing 'sensitive_action'
    # Human can inspect state, modify it, then resume with graph.invoke(None, config)
    checkpointer = MemorySaver()
    return graph.compile(
        checkpointer=checkpointer,
        interrupt_before=["sensitive_action"]
    )


# ─────────────────────────────────────────────────────────────────────────────
## MAIN: Run demonstrations
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("ADVANCED AGENTS DEMONSTRATION")
    print("=" * 60)

    # --- Demo 1: ReAct from scratch ---
    print("\n### Demo 1: ReAct Agent from Scratch ###")
    react = ReactAgent(tools=[search_web, calculate])
    answer = react.run("What is 15% of 2400? Also search for Python 3.13 news.")
    print(f"\nFinal: {answer}")

    # --- Demo 2: Multi-tool agent ---
    print("\n### Demo 2: Multi-Tool Agent ###")
    run_multi_tool_agent()

    # --- Demo 3: Structured output agent ---
    print("\n### Demo 3: Structured Output Agent ###")
    try:
        report = run_structured_output_agent("Python programming language popularity in 2025")
        print(f"\nReport: {report.model_dump_json(indent=2)}")
    except Exception as e:
        print(f"Structured output demo error: {e}")

    # --- Demo 4: Sync streaming ---
    print("\n### Demo 4: Streaming ###")
    demo_sync_streaming()

    # --- Demo 5: Persistent memory ---
    print("\n### Demo 5: Persistent Memory ###")
    demo_persistent_memory()

    # --- Demo 6: Multi-agent with LangGraph ---
    print("\n### Demo 6: Multi-Agent Graph ###")
    run_multi_agent("Search for latest Python news and calculate 2024 * 1.15")

    print("\n" + "=" * 60)
    print("All demos complete.")
    print("=" * 60)
