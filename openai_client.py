from openai import AzureOpenAI
from config import Config

openai_client = AzureOpenAI(
    azure_endpoint=Config.AZURE_OPENAI_ENDPOINT,
    api_key=Config.AZURE_OPENAI_KEY,
    api_version="2024-02-01",
)


def get_client():
    return openai_client


def create_embedding(text: str):
    response = openai_client.embeddings.create(
        input=text,
        model=Config.EMBEDDING_MODEL,
    )
    return response.data[0].embedding


def generate_answer(messages):
    response = openai_client.chat.completions.create(
        model=Config.CHAT_MODEL,
        messages=messages,
        temperature=0,
    )
    return response.choices[0].message.content


def generate_sql(question: str, schema: str) -> str:
    response = openai_client.chat.completions.create(
        model=Config.CHAT_MODEL,
        messages=[
            {
                "role": "system",
                "content": f"""You are a SQL expert. Generate a valid T-SQL query for Azure SQL Server.
Use ONLY columns that exist in the schema below.
Return ONLY the SQL query, nothing else — no explanation, no markdown, no backticks.
When filtering by company name, use LIKE instead of = for ShortName. Example: WHERE ShortName LIKE '%Microsoft%'
Schema:
{schema}""",
            },
            {"role": "user", "content": question},
        ],
        temperature=0,
    )
    return response.choices[0].message.content.strip()
