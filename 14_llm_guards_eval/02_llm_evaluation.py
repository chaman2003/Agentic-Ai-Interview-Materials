# ============================================================
# LLM EVALUATION — Test Harnesses, RAGAs, Regression Suites
# ============================================================
# pip install ragas langchain openai datasets

# Why evaluate LLMs?
# LLM outputs are non-deterministic and can degrade silently.
# Evaluation = automated tests that catch when your pipeline gets worse.

import json
from dataclasses import dataclass
from typing import Optional


# ── 1. EVALUATION DIMENSIONS ─────────────────────────────────
"""
For RAG pipelines, evaluate these 4 dimensions:

1. FAITHFULNESS  — Does the answer stick to the retrieved context?
                   (no hallucination, no made-up facts)
2. ANSWER RELEVANCY — Does the answer actually address the question?
3. CONTEXT RECALL  — Did retrieval find all relevant chunks?
4. CONTEXT PRECISION — Of retrieved chunks, how many were actually relevant?

Tools: ragas library (LLM-as-judge for all 4 metrics)
"""


# ── 2. SIMPLE MANUAL TEST HARNESS ────────────────────────────
@dataclass
class TestCase:
    query:            str
    expected_answer:  str
    context_must_contain: list[str]   # keywords that should be in retrieved context
    answer_must_contain:  list[str]   # keywords that should appear in the answer

REGRESSION_SUITE = [
    TestCase(
        query="How many disputes has the platform resolved?",
        expected_answer="millions of cases",
        context_must_contain=["disputes", "cases"],
        answer_must_contain=["cases"]
    ),
    TestCase(
        query="What is the platform's annual growth rate?",
        expected_answer="80-100% annually",
        context_must_contain=["80", "100", "annually"],
        answer_must_contain=["80"]
    ),
    TestCase(
        query="Who founded the company?",
        expected_answer=None,   # should say "I don't know" — not in context
        context_must_contain=[],
        answer_must_contain=[]
    ),
]

def run_regression_suite(rag_pipeline_fn, test_cases: list[TestCase]) -> dict:
    """
    Run a regression suite against a RAG pipeline.
    rag_pipeline_fn: function(query) -> {"answer": str, "context": str}
    """
    results = []
    passed  = 0

    for tc in test_cases:
        result = rag_pipeline_fn(tc.query)
        answer  = result.get("answer", "").lower()
        context = result.get("context", "").lower()

        # Check 1: context contains required keywords
        context_ok = all(kw.lower() in context for kw in tc.context_must_contain)

        # Check 2: answer contains required keywords
        answer_ok  = all(kw.lower() in answer  for kw in tc.answer_must_contain)

        # Check 3: for questions with no expected answer, model should express uncertainty
        if tc.expected_answer is None:
            uncertainty_phrases = ["i don't know", "not in the context", "cannot find"]
            answer_ok = any(p in answer for p in uncertainty_phrases)

        test_passed = context_ok and answer_ok
        if test_passed: passed += 1

        results.append({
            "query":       tc.query,
            "passed":      test_passed,
            "context_ok":  context_ok,
            "answer_ok":   answer_ok,
            "answer":      result.get("answer", "")[:200]
        })

    return {
        "total":   len(test_cases),
        "passed":  passed,
        "failed":  len(test_cases) - passed,
        "score":   round(passed / len(test_cases), 2),
        "results": results
    }


# ── 3. RAGAS EVALUATION ───────────────────────────────────────
"""
ragas = RAG Assessment library. Uses LLM-as-judge to score your RAG pipeline.

pip install ragas

from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_recall, context_precision
from datasets import Dataset

# Prepare evaluation dataset
eval_data = {
    "question":  ["What does the platform do?", "How many cases resolved?"],
    "answer":    [your_answers_list],
    "contexts":  [your_retrieved_contexts_list],   # list of list of strings
    "ground_truth": ["It is a legal-tech platform", "millions of cases"]
}

dataset = Dataset.from_dict(eval_data)

result = evaluate(
    dataset,
    metrics=[faithfulness, answer_relevancy, context_recall, context_precision]
)

print(result.to_pandas())
# faithfulness  answer_relevancy  context_recall  context_precision
#        0.85              0.92            0.78               0.88
"""


# ── 4. LLM-AS-JUDGE ──────────────────────────────────────────
# Use a stronger LLM to judge if a weaker LLM's output is correct
# (when you don't have ground truth)

from openai import OpenAI
client = OpenAI()

def llm_judge_faithfulness(answer: str, context: str) -> dict:
    """Use GPT-4 to judge if an answer is faithful to the context."""
    prompt = f"""Rate the faithfulness of this answer to the context.
Faithfulness = the answer only uses information from the context (no made-up facts).

Context: {context}

Answer: {answer}

Respond with JSON only:
{{
    "score": 0.0 to 1.0,
    "reasoning": "brief explanation",
    "hallucinated_claims": ["list of any claims not supported by context"]
}}"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        response_format={"type": "json_object"}
    )
    return json.loads(response.choices[0].message.content)


# ── 5. EVALUATION PIPELINE ───────────────────────────────────
def evaluate_rag_response(
    query: str,
    retrieved_context: str,
    generated_answer: str
) -> dict:
    """Complete evaluation of a single RAG response."""
    scores = {}

    # 1. Faithfulness check
    faith = llm_judge_faithfulness(generated_answer, retrieved_context)
    scores["faithfulness"] = faith["score"]
    scores["hallucinations"] = faith.get("hallucinated_claims", [])

    # 2. Length sanity check
    scores["answer_length_ok"] = 20 < len(generated_answer) < 2000

    # 3. Context used check (did the answer reference the context?)
    context_words = set(retrieved_context.lower().split())
    answer_words  = set(generated_answer.lower().split())
    overlap = len(context_words & answer_words) / max(len(context_words), 1)
    scores["context_overlap"] = round(overlap, 2)

    # Overall pass/fail
    scores["passed"] = (
        scores["faithfulness"] > 0.7 and
        scores["answer_length_ok"] and
        scores["context_overlap"] > 0.1
    )

    return scores
