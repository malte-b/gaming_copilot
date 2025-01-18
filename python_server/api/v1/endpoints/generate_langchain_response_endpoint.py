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
from langchain_core.runnables import RunnableParallel
from operator import itemgetter
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# --- internal imports
from config import TIMEZONE, DELIMITER, WEAVIATE_URL, mistral_small
from api.api_models import PromptInput

router = APIRouter()
# Load environment variables from .env
load_dotenv()


async def generate_response(prompt_input: PromptInput) -> AsyncIterable[str]:
    simple_rag_prompt = ChatPromptTemplate(
        [
            (
                "system",
                "You are a helpful AI bot. Your name is {name}. Answer the users question based on the context provided. Context: {context}",
            ),
            ("human", "{user_message}"),
        ]
    )
    string_output_rag_runnable = (
        RunnableParallel(
            {
                "name": itemgetter("name"),
                "context": itemgetter("context"),
                "user_message": itemgetter("user_message"),
            }
        )
        | simple_rag_prompt
        | mistral_small
        | StrOutputParser()
    )
    ai_msg = string_output_rag_runnable.invoke(
        input={"name": "Gaming Companion", "context": "Davids birthday is the 18th of July 1997", "user_message": prompt_input.user_message}
    )

    # 1) onStart event
    yield f"data: {json.dumps({'type': 'onStart', 'content': 'Stream is starting!', 'timestamp': datetime.now(tz=TIMEZONE).isoformat()})}{DELIMITER}"

    # 2) Text event
    yield f"data: {json.dumps({'type': 'onText', 'content': ai_msg, 'timestamp': datetime.now(tz=TIMEZONE).isoformat()})}{DELIMITER}"

    # 3) onImageUrl event
    yield f"data: {json.dumps({'type': 'onImageUrl', 'content': 'https://stardewvalleywiki.com/mediawiki/images/a/af/Horse_rider.png', 'timestamp': datetime.now(tz=TIMEZONE).isoformat()})}{DELIMITER}"

    # 5) onEnd event
    yield f"data: {json.dumps({'type': 'onEnd', 'content': 'Stream has ended.', 'timestamp': datetime.now(tz=TIMEZONE).isoformat()})}{DELIMITER}"


@router.post("/generate-langchain-response-endpoint/")
async def generate_response_handler(body: PromptInput) -> StreamingResponse:
    generator = generate_response(prompt_input=body)
    return StreamingResponse(content=generator, media_type="text/event-stream")
