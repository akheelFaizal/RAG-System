from typing import List, Dict, Tuple
import os
from prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE
from transformers import pipeline
from openai import OpenAI

# Decide which backend to use
OPENAI_KEY = os.getenv("OPENAI_API_KEY", "").strip()
USE_OPENAI = bool(OPENAI_KEY)

if USE_OPENAI:
    client = OpenAI()
else:
    print("[INFO] No valid OpenAI API key found. Using local model (distilgpt2).")
    # Load a small local language model
    generator = pipeline("text-generation", model="distilgpt2")

def build_answer_openai(question: str, contexts: List[Dict]) -> str:
    """Generate an answer using OpenAI's API."""
    ctx_text = []
    for c in contexts:
        ctx_text.append(
            f"PATH: {c['meta'].get('path','')} | LANG: {c['meta'].get('lang','')}\n{c['doc']}\n---\n"
        )
    user_prompt = USER_PROMPT_TEMPLATE.format(
        question=question, context="\n".join(ctx_text)
    )

    chat = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.2
    )
    return chat.choices[0].message.content

def build_answer_local(question: str, contexts: List[Dict]) -> str:
    """Generate an answer using a local HuggingFace model."""
    ctx_text = []
    for c in contexts:
        ctx_text.append(
            f"PATH: {c['meta'].get('path','')} | LANG: {c['meta'].get('lang','')}\n{c['doc']}\n---\n"
        )
    user_prompt = USER_PROMPT_TEMPLATE.format(
        question=question, context="\n".join(ctx_text)
    )

    prompt = f"{SYSTEM_PROMPT}\n\n{user_prompt}\nAnswer:"
    output = generator(prompt, max_length=300, num_return_sequences=1)
    return output[0]["generated_text"].replace(prompt, "").strip()

def answer_question(vstore, question: str, k: int = 5) -> Tuple[str, List[Dict]]:
    """Query the vector store and get an answer from the chosen backend."""
    docs, metas, dists = vstore.query(question, k=k)
    contexts = [{"doc": d, "meta": m, "score": 1 - dist}
                for d, m, dist in zip(docs, metas, dists)]

    if USE_OPENAI:
        answer = build_answer_openai(question, contexts)
    else:
        answer = build_answer_local(question, contexts)

    return answer, contexts
