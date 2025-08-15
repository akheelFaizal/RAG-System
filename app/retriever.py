import os
from typing import List, Dict, Tuple
import chromadb
from openai import OpenAI
from sentence_transformers import SentenceTransformer



DEFAULT_CHROMA_DIR = os.getenv("CHROMA_DIR", ".chroma")

class EmbeddingBackend:
    def __init__(self, backend=None):
        self.backend = backend or os.getenv("EMBEDDING_BACKEND", "openai")
        if self.backend == "sentence-transformers":
            model_name = os.getenv("SENTENCE_TRANSFORMER_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
            self.model = SentenceTransformer(model_name)
        else:
            self.model_name = "text-embedding-3-small"
            self.client = OpenAI()

    def embed(self, texts):
        if self.backend == "sentence-transformers":
            return self.model.encode(texts, normalize_embeddings=True).tolist()
        else:
            resp = self.client.embeddings.create(model=self.model_name, input=texts)
            return [d.embedding for d in resp.data]

class VectorStore:
    def __init__(self, collection_name: str, persist_dir: str = DEFAULT_CHROMA_DIR, embedder: EmbeddingBackend = None):
        self.client = chromadb.PersistentClient(path=persist_dir)
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        self.embedder = embedder or EmbeddingBackend()

    def add(self, ids: List[str], texts: List[str], metadatas: List[Dict]):
        embeddings = self.embedder.embed(texts)
        self.collection.add(ids=ids, embeddings=embeddings, documents=texts, metadatas=metadatas)

    def query(self, query_text: str, k: int = 5) -> Tuple[List[str], List[Dict], List[float]]:
        q_emb = self.embedder.embed([query_text])[0]
        res = self.collection.query(
            query_embeddings=[q_emb],
            n_results=k,
            include=["documents", "metadatas", "distances"]
        )
        docs = res.get("documents", [[]])[0]
        metas = res.get("metadatas", [[]])[0]
        dists = res.get("distances", [[]])[0]
        return docs, metas, dists

    def count(self) -> int:
        return self.collection.count()
