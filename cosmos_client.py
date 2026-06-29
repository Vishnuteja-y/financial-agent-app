from datetime import datetime, timezone
import uuid

from azure.cosmos import CosmosClient

from config import Config

_cosmos_client = None
_container = None


def get_container():
    global _cosmos_client, _container

    if _container:
        return _container

    _cosmos_client = CosmosClient(
        url=Config.COSMOS_URI,
        credential=Config.COSMOS_KEY,
    )

    database = _cosmos_client.get_database_client(Config.COSMOS_DB)
    _container = database.get_container_client(Config.COSMOS_CONTAINER)

    return _container


def save_turn(session_id, user_message, bot_response, retrieved_docs):
    container = get_container()

    item = {
        "id": str(uuid.uuid4()),
        "session_id": session_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "user_message": user_message,
        "bot_response": bot_response,
        "retrieved_docs": retrieved_docs,
    }

    container.upsert_item(item)


def get_history(session_id, limit=3):
    container = get_container()

    query = """
    SELECT TOP @limit *
    FROM c
    WHERE c.session_id = @session_id
    ORDER BY c.timestamp DESC
    """

    parameters = [
        {"name": "@session_id", "value": session_id},
        {"name": "@limit", "value": limit},
    ]

    items = list(
        container.query_items(
            query=query,
            parameters=parameters,
            enable_cross_partition_query=True,
        )
    )

    return list(reversed(items))


def format_history_for_prompt(session_id):
    history = get_history(session_id)

    if not history:
        return "No previous conversation."

    lines = []

    for item in history:
        lines.append(f"User: {item.get('user_message')}")
        lines.append(f"Assistant: {item.get('bot_response')}")

    return "\n".join(lines)