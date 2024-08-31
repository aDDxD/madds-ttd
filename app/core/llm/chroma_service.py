from typing import List

import chromadb
from sentence_transformers import SentenceTransformer

from app.core.utils.logger import Logger


class ChromaService:
    def __init__(self, collection_name="schema_collection"):
        self.logger = Logger(self.__class__.__name__).get_logger()

        self.client = chromadb.PersistentClient(path="chromadb")
        self.collection = self.client.get_or_create_collection(name=collection_name)
        self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

    def add_schema_vectors(self, schema_data: List[str]):
        try:
            embeddings = self.embedding_model.encode(
                schema_data, convert_to_tensor=False
            ).tolist()

            ids = [f"doc_{i}" for i in range(len(schema_data))]

            self.logger.info("Adding schema vectors to ChromaDB collection...")

            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=schema_data,
            )

            self.logger.info("Schema vectors added to ChromaDB successfully.")

        except Exception as e:
            self.logger.error("Error adding schema vectors to ChromaDB: %s", str(e))

    def query_schema(self, query_text: str):
        try:
            query_embeddings = self.embedding_model.encode(
                [query_text], convert_to_tensor=False
            ).tolist()

            self.logger.info("Querying ChromaDB with embeddings for RAG...")

            results = self.collection.query(query_embeddings=query_embeddings)

            documents = results.get("documents", [[]])[0]
            extracted_results = [{"text": doc} for doc in documents]

            self.logger.info("Schema information retrieved from ChromaDB successfully.")

            return extracted_results

        except Exception as e:
            self.logger.error("Error querying schema from ChromaDB: %s", str(e))
            return []
