from pinecone import Pinecone
from langchain_pinecone import PineconeVectorStore
from langchain_core.documents import Document
from uuid import uuid4
from typing import List
from pydantic import BaseModel, RootModel
import json

# --- internal imports
from config import PINECONE_API_KEY, mistral_embeddings


class Metadata(BaseModel):
    title: str
    category: str


class PageData(BaseModel):
    page_content: str
    metadata: Metadata


class StardewPages(RootModel[List[PageData]]):
    # Optionally implement an __iter__ for convenience
    def __iter__(self):
        return iter(self.root)


def read_and_validate_stardew_pages(json_filename: str) -> StardewPages:
    """
    Reads the JSON file specified by `json_filename` and validates
    it against the StardewPages Pydantic model.
    Returns a StardewPages instance.
    """
    with open(json_filename, "r", encoding="utf-8") as f:
        data = json.load(f)
    # Use model_validate for Pydantic v2
    stardew_pages = StardewPages.model_validate(data)
    return stardew_pages


def convert_stardew_pages_to_documents(stardew_pages: StardewPages) -> List[Document]:
    """
    Converts validated StardewPages data into a list of LangChain Document objects.
    """
    docs = []
    # Either iterate over stardew_pages.root
    # or rely on the __iter__ implementation shown above
    for page in stardew_pages:
        doc = Document(page_content=page.page_content, metadata={"title": page.metadata.title, "category": page.metadata.category})
        docs.append(doc)
    return docs


def ingest_data_into_pinecone():
    pc = Pinecone(api_key=PINECONE_API_KEY)
    index = pc.Index(name="gaming-copilot", host="https://gaming-copilot-mipa415.svc.aped-4627-b74a.pinecone.io")
    vector_store = PineconeVectorStore(index=index, embedding=mistral_embeddings)

    stardew_pages = read_and_validate_stardew_pages("dummy_data.json")
    documents = convert_stardew_pages_to_documents(stardew_pages)
    uuids = [str(uuid4()) for _ in range(len(documents))]
    print(f"Adding {len(documents)} documents.")
    vector_store.add_documents(documents=documents, ids=uuids)


if __name__ == "__main__":
    ingest_data_into_pinecone()
