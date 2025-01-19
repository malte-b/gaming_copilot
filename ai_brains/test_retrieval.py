import os
import weaviate
from weaviate.auth import AuthApiKey
from dotenv import load_dotenv
from mistralai import Mistral



load_dotenv()

WEAVIATE_URL = os.getenv("WEAVIATE_URL")
WEAVIATE_API_KEY = os.getenv("WEAVIATE_API_KEY")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

def run_mistral(user_message, model="mistral-large-latest"):
    client = Mistral(api_key=MISTRAL_API_KEY)
    messages = [
        {
            "role": "user", "content": user_message
        }
    ]
    chat_response = client.chat.complete(
        model=model,
        messages=messages
    )
    return (chat_response.choices[0].message.content)

client = weaviate.connect_to_weaviate_cloud(
    cluster_url=WEAVIATE_URL,
    auth_credentials=AuthApiKey(WEAVIATE_API_KEY),
    headers={
        "X-Mistral-Api-Key": MISTRAL_API_KEY
    }
)
chunks = client.collections.get("StardewWiki")
retrieved_documents = chunks.query.near_text(
            query="What gifts does Linus love?", 
            limit=3)
client.close()

prompt = f"""
        Context information is below.
        ---------------------
        {retrieved_documents}
        ---------------------
        Given the context information and not prior knowledge, answer the query.
        Query: What gifts does Linus love?
        Answer:
    """
ai_msg = run_mistral(prompt)

print(ai_msg)