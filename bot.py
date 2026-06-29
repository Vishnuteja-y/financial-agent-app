import json
import logging

from botbuilder.core import ActivityHandler, TurnContext, MessageFactory

from search_client import search_financial_data
from cosmos_client import save_turn, format_history_for_prompt
from openai_client import generate_answer, generate_sql
from sql_client import run_sql_query, SCHEMA
from router import route_query

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """
You are a financial analyst AI for TechStarGroup.

Rules:
1. Answer using the provided retrieved data.
2. If the data contains a number, always include it in your answer.
3. Do not say data is missing if a value is present in the retrieved data.
4. Keep the answer clear and business-friendly.
5. For revenue numbers, format them in billions (e.g. $184.9 billion).
"""


def build_messages(question: str, history: str, documents: list):
    context = json.dumps(documents, indent=2, default=str)
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": f"""
Conversation history:
{history}

Retrieved financial data:
{context}

User question:
{question}
""",
        },
    ]


def answer_question(question: str, session_id: str = "web-session"):
    history = format_history_for_prompt(session_id)

    # Router decides RAG or SQL
    route = route_query(question)

    if route == "SQL":
        logger.info("[Router] Using Text-to-SQL path")
        sql = generate_sql(question, SCHEMA)
        logger.info(f"[SQL] Generated query: {sql}")
        documents = run_sql_query(sql)
    else:
        logger.info("[Router] Using RAG path")
        documents = search_financial_data(question, top_k=5)

    messages = build_messages(question, history, documents)
    answer = generate_answer(messages)

    save_turn(session_id, question, answer, documents)

    return {
        "answer": answer,
        "sources": documents,
        "route": route,
    }


class FinancialBot(ActivityHandler):
    async def on_message_activity(self, turn_context: TurnContext):
        user_message = turn_context.activity.text
        session_id = turn_context.activity.conversation.id

        try:
            result = answer_question(user_message, session_id)
            await turn_context.send_activity(MessageFactory.text(result["answer"]))

        except Exception as e:
            logger.exception("Bot processing failed")
            await turn_context.send_activity(
                MessageFactory.text("Sorry, I had trouble processing that request.")
            )

    async def on_members_added_activity(self, members_added, turn_context: TurnContext):
        for member in members_added:
            if member.id != turn_context.activity.recipient.id:
                await turn_context.send_activity(
                    MessageFactory.text(
                        "Welcome to Financial AI. Ask me about company revenue, margins, or financial performance."
                    )
                )
