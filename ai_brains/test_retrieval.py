import os
import weaviate
from weaviate.auth import AuthApiKey
from dotenv import load_dotenv



load_dotenv()

WEAVIATE_URL = os.getenv("WEAVIATE_URL")
WEAVIATE_API_KEY = os.getenv("WEAVIATE_API_KEY")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

client = weaviate.connect_to_weaviate_cloud(
    cluster_url=WEAVIATE_URL,
    auth_credentials=AuthApiKey(WEAVIATE_API_KEY),
    headers={
        "X-Mistral-Api-Key": MISTRAL_API_KEY
    }
)
chunks = client.collections.get("StardewWiki")
retrieved_documents = chunks.query.near_text(
            query="What gifts does Linus love??", 
            limit=3)
client.close()

print(retrieved_documents)