from pinecone import Pinecone
from langchain_pinecone import PineconeVectorStore

# --- internal imports
from config import PINECONE_API_KEY, mistral_embeddings


def delete_data_from_pinecone():
    pc = Pinecone(api_key=PINECONE_API_KEY)
    index = pc.Index(name="gaming-copilot", host="https://gaming-copilot-mipa415.svc.aped-4627-b74a.pinecone.io")
    vector_store = PineconeVectorStore(index=index, embedding=mistral_embeddings)
    vector_store.delete(delete_all=True)


# poetry run python pinecone_deletion.py
if __name__ == "__main__":
    delete_data_from_pinecone()
