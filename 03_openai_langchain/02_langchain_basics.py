# ============================================================
# LANGCHAIN BASICS — Interview Essentials
# ============================================================
# pip install langchain langchain-openai

import os
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain

# ── LLM SETUP ────────────────────────────────────────────────
llm = ChatOpenAI(
    model="gpt-4",
    temperature=0.7,
    openai_api_key=os.environ.get("OPENAI_API_KEY")
)


# ── PROMPT TEMPLATES ─────────────────────────────────────────
# Reusable prompts with variables (like f-strings but for LLMs)

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant that explains {topic} clearly."),
    ("human",  "{question}")
])

# Manually format (for understanding)
formatted = prompt.format_messages(topic="Python", question="What is a generator?")
print(formatted)


# ── LCEL PIPE SYNTAX ─────────────────────────────────────────
# Modern LangChain: chain = prompt | llm | parser
# Each | pipes output of one into input of next

basic_chain = prompt | llm | StrOutputParser()

# Run the chain
result = basic_chain.invoke({
    "topic": "Python",
    "question": "Explain decorators in simple terms"
})
print(result)


# ── OUTPUT PARSERS ────────────────────────────────────────────

# 1. StrOutputParser — returns raw text
str_chain = prompt | llm | StrOutputParser()

# 2. JsonOutputParser — parses response as JSON dict
json_prompt = ChatPromptTemplate.from_messages([
    ("system", "You extract data as JSON only. No explanation."),
    ("human",  "Extract name and age from: {text}")
])
json_chain = json_prompt | llm | JsonOutputParser()

# result = json_chain.invoke({"text": "My name is Chaman, I am 21"})
# print(result)  # {'name': 'Chaman', 'age': 21}

# 3. PydanticOutputParser — parse into a typed Python object
class PersonInfo(BaseModel):
    name: str = Field(description="Person's full name")
    age:  int = Field(description="Person's age")
    city: str = Field(description="Person's city", default="Unknown")

from langchain.output_parsers import PydanticOutputParser
pydantic_parser = PydanticOutputParser(pydantic_object=PersonInfo)

pydantic_prompt = ChatPromptTemplate.from_messages([
    ("system", "Extract person info. {format_instructions}"),
    ("human",  "{text}")
]).partial(format_instructions=pydantic_parser.get_format_instructions())

pydantic_chain = pydantic_prompt | llm | pydantic_parser

# result = pydantic_chain.invoke({"text": "Chaman is a 21yo from Bangalore"})
# print(result.name)  # "Chaman"
# print(result.age)   # 21


# ── CONVERSATION MEMORY ───────────────────────────────────────
# ConversationBufferMemory: stores ALL messages and adds them to every prompt

memory = ConversationBufferMemory()
conversation = ConversationChain(llm=llm, memory=memory, verbose=True)

# response1 = conversation.predict(input="My name is Chaman")
# response2 = conversation.predict(input="What's my name?")  # will remember!


# ── MULTIPLE CHAIN COMPOSITION ────────────────────────────────
# Chain 1: Generate a question
question_prompt = ChatPromptTemplate.from_template("Generate one interview question about: {topic}")
question_chain = question_prompt | llm | StrOutputParser()

# Chain 2: Answer the question
answer_prompt = ChatPromptTemplate.from_template("Answer this interview question: {question}")
answer_chain = answer_prompt | llm | StrOutputParser()

# Compose — output of first chain goes into second
def question_and_answer(topic):
    question = question_chain.invoke({"topic": topic})
    answer   = answer_chain.invoke({"question": question})
    return {"question": question, "answer": answer}


# ── INTERVIEW SUMMARY ────────────────────────────────────────
"""
Q: What is LangChain?
A: A framework for building LLM applications. It handles prompt templates,
   chaining LLM calls, output parsing, memory, agents, and RAG.

Q: What is LCEL?
A: LangChain Expression Language. Pipe syntax (|) to compose chains.
   `chain = prompt | llm | parser` → `chain.invoke({"input": "..."})`

Q: What are output parsers?
A: Convert raw LLM text output into structured Python objects.
   StrOutputParser → raw text
   JsonOutputParser → dict
   PydanticOutputParser → typed Pydantic model

Q: What is ConversationBufferMemory?
A: Stores the full conversation history and adds it to every prompt,
   so the model "remembers" previous messages.

Q: Chains vs Agents?
A: Chains are fixed sequences of steps — you define the order.
   Agents are dynamic — the LLM decides which tools to use and in what order.
"""
