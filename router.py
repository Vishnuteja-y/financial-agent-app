from openai_client import get_client
from config import Config

ROUTING_PROMPT = """
You are a query router for a financial data system.
Decide if the user question should use RAG (vector search) or SQL (exact database query).

Use SQL when:
- User asks for exact numbers (revenue, margins, ratios)
- User asks to compare specific companies
- User asks for rankings (top 5, highest, lowest)
- User asks for aggregations (average, total, sum)

Use RAG when:
- User asks broad/conceptual questions
- User asks about trends or analysis
- Question is conversational or unclear

Reply with ONLY one word: SQL or RAG
"""


def route_query(question: str) -> str:
    client = get_client()
    response = client.chat.completions.create(
        model=Config.CHAT_MODEL,
        messages=[
            {"role": "system", "content": ROUTING_PROMPT},
            {"role": "user", "content": question},
        ],
        max_tokens=5,
        temperature=0,
    )
    decision = response.choices[0].message.content.strip().upper()
    print(f"[Router] Question: '{question}' → {decision}", flush=True)
    return decision if decision in ["SQL", "RAG"] else "RAG"
