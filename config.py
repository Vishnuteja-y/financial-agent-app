import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
    AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")
    CHAT_MODEL = os.getenv("CHAT_MODEL", "gpt-4.1-mini")
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")

    SEARCH_ENDPOINT = os.getenv("SEARCH_ENDPOINT")
    SEARCH_KEY = os.getenv("SEARCH_KEY")
    SEARCH_INDEX = os.getenv("SEARCH_INDEX")
    SEARCH_VECTOR_FIELD = os.getenv("SEARCH_VECTOR_FIELD", "text_vector")

    COSMOS_URI = os.getenv("COSMOS_URI")
    COSMOS_KEY = os.getenv("COSMOS_KEY")
    COSMOS_DB = os.getenv("COSMOS_DB", "financial-agent-db")
    COSMOS_CONTAINER = os.getenv("COSMOS_CONTAINER", "conversations")

    # Azure SQL
    SQL_SERVER = os.getenv("SQL_SERVER")
    SQL_DATABASE = os.getenv("SQL_DATABASE", "financial-gold-db")
    SQL_USER = os.getenv("SQL_USER", "sqladmin")
    SQL_PASSWORD = os.getenv("SQL_PASSWORD")

    MicrosoftAppType = os.getenv("MicrosoftAppType", "")
    MicrosoftAppId = os.getenv("MicrosoftAppId", "")
    MicrosoftAppPassword = os.getenv("MicrosoftAppPassword", "")
    MicrosoftAppTenantId = os.getenv("MicrosoftAppTenantId", "")

    @staticmethod
    def validate():
        required = [
            "AZURE_OPENAI_ENDPOINT",
            "AZURE_OPENAI_KEY",
            "SEARCH_ENDPOINT",
            "SEARCH_KEY",
            "SEARCH_INDEX",
        ]

        missing = [name for name in required if not os.getenv(name)]
        if missing:
            raise RuntimeError(f"Missing environment variables: {missing}")
