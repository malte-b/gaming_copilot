import os
import json
from tqdm import tqdm
import weaviate
from weaviate.auth import AuthApiKey
from weaviate.classes.config import Configure, Property, DataType
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

def chunk_text_with_overlap(text, max_words, max_word_length=50, overlap=0.2):
    words = text.split()
    words = [word for word in words if len(word) <= max_word_length]
    chunks = []
    step = int(max_words * (1 - overlap))
    
    for i in range(0, len(words), step):
        chunk = words[i:i + max_words]
        if chunk:
            chunk_text = ' '.join(chunk)
            if len(chunk_text) <= 6000:  # Added safety margin below 8192 (Mistrals max embedding size)
                chunks.append(chunk_text)
    
    return chunks

try:
    # delete collection if it already exists
    if "StardewWiki" in client.collections.list_all():
        client.collections.delete("StardewWiki")
    if "StardewWiki" not in client.collections.list_all():
        client.collections.create(
            name="StardewWiki",
            vectorizer_config=Configure.Vectorizer.text2vec_mistral(),
            properties=[
                Property(
                    name="page_content",
                    data_type=DataType.TEXT,
                    vectorize_property_name=True
                ),
                Property(
                    name="title",
                    data_type=DataType.TEXT
                ),
                Property(
                    name="categories",
                    data_type=DataType.TEXT_ARRAY
                )
            ]
        )
    collection = client.collections.get("StardewWiki")

    json_data = json.load(open("cleaned_stardew_wiki.json", 'r', encoding='utf-8'))

    with collection.batch.dynamic() as batch:
        for item in tqdm(json_data):
            content_chunks = chunk_text_with_overlap(
                                item["page_content"], 
                                max_words=100, 
                                overlap=0.2)
            for chunk in content_chunks:
                batch.add_object(
                    properties={
                        "page_content": item["page_content"],
                        "title": item["metadata"]["title"],
                        "categories": item["metadata"]["categories"]
                    }
                )
        failed_objs_a = client.batch.failed_objects  # Get failed objects from the first batch import
        failed_refs_a = client.batch.failed_references  # Get failed references from the first batch import
        if failed_objs_a:
            print(f"Failed objects in first batch: {failed_objs_a}")
        if failed_refs_a:   
            print(f"Failed references in first batch: {failed_refs_a}")
except Exception as e:
    print(e)
finally:
    client.close()

