# --- external imports
import json
from datetime import datetime
from typing import AsyncIterable
from fastapi.routing import APIRouter
from fastapi.responses import StreamingResponse
from haystack_integrations.document_stores.weaviate import WeaviateDocumentStore, AuthApiKey
from haystack import Document
from haystack.components.builders import ChatPromptBuilder
from haystack_integrations.components.embedders.mistral import MistralTextEmbedder
from haystack_integrations.components.retrievers.weaviate import WeaviateEmbeddingRetriever
from haystack_integrations.components.generators.mistral import MistralChatGenerator
from haystack import Pipeline
from haystack.dataclasses import ChatMessage
from dotenv import load_dotenv


# --- internal imports
from config import TIMEZONE, DELIMITER, WEAVIATE_URL
from api.api_models import PromptInput

router = APIRouter()
# Load environment variables from .env
load_dotenv()


async def generate_response(prompt_input: PromptInput) -> AsyncIterable[str]:
    auth_client_secret = AuthApiKey()
    document_store = WeaviateDocumentStore(url=WEAVIATE_URL, auth_client_secret=auth_client_secret)

    message_template = """
    Answer the users question based on the context provided.
    Each retreived context chunk is followed by the URL it comes from.
    Reference the URLs from which your answer is generated.

    Context:
    {% for doc in documents %}
    Content: {{doc.content}}
    URL: {{doc.meta['url']}}
    {% endfor %}
    Qyestion: {{query}}
    """

    referenced_rag = Pipeline()
    referenced_rag.add_component("query_embedder", MistralTextEmbedder())
    referenced_rag.add_component("retriever", WeaviateEmbeddingRetriever(document_store=document_store))
    referenced_rag.add_component("prompt", ChatPromptBuilder(variables=["documents"]))
    referenced_rag.add_component("llm", MistralChatGenerator(model="mistral-small-latest"))

    referenced_rag.connect("query_embedder.embedding", "retriever.query_embedding")
    referenced_rag.connect("retriever.documents", "prompt.documents")
    referenced_rag.connect("prompt.prompt", "llm.messages")

    print("Response generation started...")
    messages = [ChatMessage.from_user(message_template)]
    result = referenced_rag.run(
        {
            "query_embedder": {"text": prompt_input.user_message},
            "retriever": {"top_k": 5},
            "prompt": {"template_variables": {"query": prompt_input.user_message}, "template": messages},
        }
    )
    print(result["retriever"]["documents"])

    # 1) onStart event
    yield f"data: {json.dumps({'type': 'onStart', 'content': 'Stream is starting!', 'timestamp': datetime.now(tz=TIMEZONE).isoformat()})}{DELIMITER}"

    # 2) Text event
    yield f"data: {json.dumps({'type': 'onText', 'content': result['llm']['replies'][0]._content[0].text, 'timestamp': datetime.now(tz=TIMEZONE).isoformat()})}{DELIMITER}"

    # 3) onImageUrl event
    yield f"data: {json.dumps({'type': 'onImageUrl', 'content': 'https://stardewvalleywiki.com/mediawiki/images/a/af/Horse_rider.png', 'timestamp': datetime.now(tz=TIMEZONE).isoformat()})}{DELIMITER}"

    # 5) onEnd event
    yield f"data: {json.dumps({'type': 'onEnd', 'content': 'Stream has ended.', 'timestamp': datetime.now(tz=TIMEZONE).isoformat()})}{DELIMITER}"


@router.post("/generate-langchain-response-endpoint/")
async def generate_response_handler(body: PromptInput) -> StreamingResponse:
    generator = generate_response(prompt_input=body)
    return StreamingResponse(content=generator, media_type="text/event-stream")
