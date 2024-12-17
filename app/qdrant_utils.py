import os
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from langchain_qdrant import QdrantVectorStore
from langchain_ollama import OllamaEmbeddings


URL = os.getenv("QDRANT_URL")
API_KEY = os.getenv("QDRANT_API_KEY")
COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME")

client = QdrantClient(url=URL, api_key=API_KEY)

embedding_model = OllamaEmbeddings(model="nomic-embed-text")
vectorstore = QdrantVectorStore(
    client=client, collection_name=COLLECTION_NAME, embedding=embedding_model
)


def initialize_qdrant():
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=768, distance=Distance.COSINE),
    )
