import pytz
import os
from dotenv import load_dotenv
from langchain_mistralai import ChatMistralAI
from langchain_mistralai import MistralAIEmbeddings

# Load environment variables from .env
load_dotenv()

# delimiter for SSE
DELIMITER = "---END OF EVENT---\n\n"

berlin_tz = pytz.timezone("Europe/Berlin")
TIMEZONE = berlin_tz

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
WEAVIATE_API_KEY = os.getenv("WEAVIATE_API_KEY")
WEAVIATE_URL = os.getenv("WEAVIATE_URL")

mistral_small = ChatMistralAI(model="mistral-small-latest", temperature=0, api_key=MISTRAL_API_KEY)
mistral_embeddings = MistralAIEmbeddings(model="mistral-embed", api_key=MISTRAL_API_KEY)

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
