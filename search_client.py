from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery

from config import Config
from openai_client import create_embedding

search_client = SearchClient(
    endpoint=Config.SEARCH_ENDPOINT,
    index_name=Config.SEARCH_INDEX,
    credential=AzureKeyCredential(Config.SEARCH_KEY),
)


def search_financial_data(question: str, top_k: int = 5):
    question_vector = create_embedding(question)

    vector_query = VectorizedQuery(
        vector=question_vector,
        k_nearest_neighbors=top_k,
        fields=Config.SEARCH_VECTOR_FIELD,
    )

    results = search_client.search(
        search_text=question,
        vector_queries=[vector_query],
        top=top_k,
    )

    documents = []

    for result in results:
        doc = dict(result)

        # Remove vector fields from GPT context
        doc.pop(Config.SEARCH_VECTOR_FIELD, None)
        doc.pop("@search.score", None)
        doc.pop("@search.reranker_score", None)

        documents.append(doc)

    return documents