# ============================================================
# OPENAI API BASICS — Interview Essentials
# ============================================================
# pip install openai tenacity

import os
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# ── BASIC CHAT COMPLETION ─────────────────────────────────────
def ask(question):
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user",   "content": question}
        ],
        temperature=0.7,    # 0=deterministic, 1=creative
        max_tokens=500      # limit response length → control costs
    )
    return response.choices[0].message.content

# print(ask("What is RAG in AI?"))


# ── CONVERSATION WITH HISTORY ─────────────────────────────────
def chat_with_history():
    messages = [
        {"role": "system", "content": "You are a helpful tutor."}
    ]

    while True:
        user_input = input("You: ")
        if user_input.lower() in ["quit", "exit"]:
            break

        messages.append({"role": "user", "content": user_input})

        response = client.chat.completions.create(
            model="gpt-4",
            messages=messages
        )

        ai_reply = response.choices[0].message.content
        messages.append({"role": "assistant", "content": ai_reply})
        print(f"AI: {ai_reply}")


# ── TEMPERATURE ───────────────────────────────────────────────
# temperature=0   → same answer every time → use for data extraction
# temperature=0.7 → some creativity → use for writing, chat
# temperature=1   → very creative/random → use for brainstorming

def extract_structured_data(text):
    """Use temperature=0 for consistent extraction"""
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Extract name and age from text. Reply only with JSON."},
            {"role": "user", "content": text}
        ],
        temperature=0   # deterministic!
    )
    return response.choices[0].message.content

# extract_structured_data("My name is Chaman and I am 21 years old")


# ── FUNCTION / TOOL CALLING ───────────────────────────────────
# You define a JSON schema for a function.
# The model decides if and when to call it, and returns structured JSON.
# Used for: controlled data extraction, calling real APIs based on user intent.

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_case_info",
            "description": "Retrieve information about a legal case by its ID",
            "parameters": {
                "type": "object",
                "properties": {
                    "case_id": {
                        "type": "string",
                        "description": "The unique case identifier"
                    },
                    "include_documents": {
                        "type": "boolean",
                        "description": "Whether to include related documents"
                    }
                },
                "required": ["case_id"]
            }
        }
    }
]

def call_with_tool(user_message):
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": user_message}],
        tools=tools,
        tool_choice="auto"   # model decides when to use the tool
    )

    if response.choices[0].message.tool_calls:
        tool_call = response.choices[0].message.tool_calls[0]
        print(f"Model wants to call: {tool_call.function.name}")
        print(f"With args: {tool_call.function.arguments}")   # JSON string
    return response


# ── EMBEDDINGS ────────────────────────────────────────────────
def get_embedding(text):
    response = client.embeddings.create(
        model="text-embedding-ada-002",
        input=text
    )
    return response.data[0].embedding   # list of 1536 floats


# ── ERROR HANDLING WITH RETRY ─────────────────────────────────
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10)
)
def robust_call(prompt):
    """Retry up to 3 times on failure, with exponential backoff"""
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"API error: {e}")
        raise   # re-raise so tenacity can retry


# ── STREAMING RESPONSE ────────────────────────────────────────
def stream_response(prompt):
    """Stream the response token by token"""
    stream = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        stream=True
    )
    for chunk in stream:
        if chunk.choices[0].delta.content:
            print(chunk.choices[0].delta.content, end="", flush=True)
    print()  # newline at end


# ── INTERVIEW SUMMARY ────────────────────────────────────────
"""
Q: What is the OpenAI API?
A: An HTTP API to a language model. You send a list of messages (conversation history),
   it returns a text response. Works over HTTP — same as calling any REST API.

Q: What is temperature?
A: Controls randomness. 0 = always same answer (deterministic). 1 = very creative/random.
   Use 0 for structured extraction, 0.7 for chat/generation.

Q: What is function calling?
A: You define a function schema (name, description, parameters) in JSON.
   The model decides when to call it and returns structured JSON with the arguments.
   You then call the actual function and can feed the result back to the model.

Q: Why use max_tokens?
A: To limit response length and control API costs. Long responses cost more.

Q: How do you handle API errors?
A: Wrap every call in try/except. Use tenacity library for automatic retries
   with exponential backoff on transient errors (rate limits, network issues).
"""
