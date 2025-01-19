# --- external imports
import json
from datetime import datetime
from typing import AsyncIterable, List
from fastapi.routing import APIRouter
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv
from langchain_core.documents.base import Document
from langchain_core.runnables import RunnableParallel
from operator import itemgetter
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from pinecone import Pinecone
from langchain_pinecone import PineconeVectorStore
import os
import weaviate
from weaviate.auth import AuthApiKey
from mistralai import Mistral


# --- internal imports
from config import TIMEZONE, DELIMITER, mistral_small, mistral_embeddings, PINECONE_API_KEY
from api.api_models import PromptInput

router = APIRouter()
# Load environment variables from .env
load_dotenv()

WEAVIATE_URL = os.getenv("WEAVIATE_URL")
WEAVIATE_API_KEY = os.getenv("WEAVIATE_API_KEY")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")


async def retrieve_with_weaviate(prompt_input: PromptInput) -> List[Document]:
    # RETRIEVAL
    client = weaviate.connect_to_weaviate_cloud(
        cluster_url=WEAVIATE_URL, auth_credentials=AuthApiKey(WEAVIATE_API_KEY), headers={"X-Mistral-Api-Key": MISTRAL_API_KEY}
    )
    chunks = client.collections.get("StardewWiki")
    retrieved_documents = chunks.query.near_text(query=prompt_input.user_message, limit=3)
    client.close()
    return retrieved_documents


async def retrieve_with_pinecone(prompt_input: PromptInput) -> List[Document]:
    # RETRIEVAL
    pc = Pinecone(api_key=PINECONE_API_KEY)
    index = pc.Index(name="gaming-copilot", host="https://gaming-copilot-mipa415.svc.aped-4627-b74a.pinecone.io")
    vector_store = PineconeVectorStore(index=index, embedding=mistral_embeddings)
    retrieved_documents: List[Document] = vector_store.similarity_search(
        query=prompt_input.user_message,
        k=3,
        # filter={"source": "tweet"},
    )
    print(
        f"""
          Retrieved documents: 
          {retrieved_documents}
          """
    )
    return retrieved_documents


def run_mistral(user_message, model="mistral-large-latest"):
    client = Mistral(api_key=MISTRAL_API_KEY)
    system_message = """
        You are a helpful, friendly and witty video game assistant for the game 'Stardew Valley'.
        Your name is 'Stardew Wizard'.
        You will receive a question from a user and some context from the 'Stardew Valley Wiki' to answer that question.
        Anwer the user question only based on the context from the wiki without referring to the context in your answer.
    """
    messages = [{"role": "system", "content": system_message}, {"role": "user", "content": user_message}]
    chat_response = client.chat.complete(model=model, messages=messages)
    return chat_response.choices[0].message.content


async def generate_response_with_weaviate(prompt_input: PromptInput) -> AsyncIterable[str]:
    retrieved_documents = await retrieve_with_weaviate(prompt_input)
    prompt = f"""
        Context information is below.
        ---------------------
        {retrieved_documents}
        ---------------------
        User question: {prompt_input.user_message}
        Your Answer:
    """
    ai_msg = run_mistral(prompt)
    # 1) onStart event
    yield f"data: {json.dumps({'type': 'onStart', 'content': 'Stream is starting!', 'timestamp': datetime.now(tz=TIMEZONE).isoformat()})}{DELIMITER}"

    # 2) onImageUrl event
    yield f"data: {json.dumps({'type': 'onImageUrl', 'content': 'https://stardewvalleywiki.com/mediawiki/images/c/c7/Wizard.png', 'timestamp': datetime.now(tz=TIMEZONE).isoformat()})}{DELIMITER}"

    # 3) Text event
    yield f"data: {json.dumps({'type': 'onText', 'content': ai_msg, 'timestamp': datetime.now(tz=TIMEZONE).isoformat()})}{DELIMITER}"

    # 5) onEnd event
    yield f"data: {json.dumps({'type': 'onEnd', 'content': 'Stream has ended.', 'timestamp': datetime.now(tz=TIMEZONE).isoformat()})}{DELIMITER}"


async def generate_response_with_pinecone(prompt_input: PromptInput) -> AsyncIterable[str]:
    # RETRIEVAL
    pc = Pinecone(api_key=PINECONE_API_KEY)
    index = pc.Index(name="gaming-copilot", host="https://gaming-copilot-mipa415.svc.aped-4627-b74a.pinecone.io")
    vector_store = PineconeVectorStore(index=index, embedding=mistral_embeddings)
    retrieved_documents: List[Document] = vector_store.similarity_search(
        query=prompt_input.user_message,
        k=3,
        # filter={"source": "tweet"},
    )
    print(
        f"""
          Retrieved documents: 
          {retrieved_documents}
          """
    )

    # GENERATION
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
        input={"name": "Gaming Companion", "context": retrieved_documents, "user_message": prompt_input.user_message}
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
    if body.use_pinecone:
        generator = generate_response_with_pinecone(prompt_input=body)
    else:
        generator = generate_response_with_weaviate(prompt_input=body)
    return StreamingResponse(content=generator, media_type="text/event-stream")
