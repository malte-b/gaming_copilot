import os
from dotenv import load_dotenv
from haystack_integrations.document_stores.weaviate import (
    WeaviateDocumentStore,
    AuthApiKey,
)
from haystack import Document
from haystack import Pipeline
from haystack_integrations.components.embedders.mistral import MistralDocumentEmbedder
from haystack.components.fetchers import LinkContentFetcher
from haystack.components.converters import HTMLToDocument
from haystack.components.converters import TikaDocumentConverter
from haystack.components.preprocessors import DocumentCleaner, DocumentSplitter
from haystack.components.writers import DocumentWriter
from pathlib import Path

load_dotenv()

auth_client_secret = AuthApiKey()

document_store = WeaviateDocumentStore(
    url=os.getenv("WEAVIATE_URL"), auth_client_secret=auth_client_secret
)

index_to_weaviate = Pipeline()

# index_to_weaviate.add_component("fetcher", LinkContentFetcher())
index_to_weaviate.add_component("converter", TikaDocumentConverter())
index_to_weaviate.add_component("cleaner", DocumentCleaner())
index_to_weaviate.add_component("splitter", DocumentSplitter())
index_to_weaviate.add_component("embedder", MistralDocumentEmbedder())
index_to_weaviate.add_component("writer", DocumentWriter(document_store))


# index_to_weaviate.connect("fetcher", "converter")
index_to_weaviate.connect("converter", "cleaner")
index_to_weaviate.connect("cleaner", "splitter")
index_to_weaviate.connect("splitter", "embedder")
index_to_weaviate.connect("embedder", "writer")

index_to_weaviate.run({"converter": {"sources": [Path("data/stardewvalleywikicom_mediawiki-20250118-current.xml")]}})
