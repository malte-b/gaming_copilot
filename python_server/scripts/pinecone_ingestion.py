import json
import uuid
from typing import List

from langchain_core.documents import Document
from pinecone import Pinecone
from langchain_pinecone import PineconeVectorStore

# -- internal imports
from config import PINECONE_API_KEY, mistral_embeddings


def read_stardew_pages_no_validation(json_filename: str) -> List[dict]:
    """
    Simply loads the JSON and returns it as a list of dicts
    without any Pydantic validation or field manipulation.
    """
    with open(json_filename, "r", encoding="utf-8") as f:
        data = json.load(f)
    # e.g. data is [ { "markdown": "...", "metadata": {...} }, ... ]
    return data


def convert_to_documents_no_validation(stardew_data: List[dict]) -> List[Document]:
    """
    Takes the raw list of dicts and converts them to LangChain Document objects.
    The 'markdown' field becomes page_content; the 'metadata' field stays as metadata.
    """
    docs = []
    for item in stardew_data:
        # Safely get your fields
        markdown = item.get("markdown", "")
        metadata = item.get("metadata", {})

        # Create the Document
        doc = Document(page_content=markdown, metadata=metadata)
        docs.append(doc)
    return docs


def ingest_data_into_pinecone_no_validation(json_filename: str = "scraped_data.json"):
    # Initialize Pinecone connection
    pc = Pinecone(api_key=PINECONE_API_KEY)
    index = pc.Index(
        name="gaming-copilot",
        host="https://gaming-copilot-mipa415.svc.aped-4627-b74a.pinecone.io",
    )
    vector_store = PineconeVectorStore(index=index, embedding=mistral_embeddings)

    # Load raw JSON and convert to Documents
    stardew_data = read_stardew_pages_no_validation(json_filename)
    documents = convert_to_documents_no_validation(stardew_data)

    # Generate unique IDs for each Document
    doc_ids = [str(uuid.uuid4()) for _ in range(len(documents))]

    print(f"Adding {len(documents)} documents to Pinecone.")
    vector_store.add_documents(documents=documents, ids=doc_ids)


# poetry run python -m scripts.pinecone_ingestion
if __name__ == "__main__":
    ingest_data_into_pinecone_no_validation()
