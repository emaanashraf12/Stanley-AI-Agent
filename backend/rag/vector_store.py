from pathlib import Path

import chromadb
from chromadb.config import Settings


class VectorStore:

    def __init__(self, collection_name="stanley_tours"):

        project_root = Path(__file__).resolve().parent.parent.parent

        self.client = chromadb.PersistentClient(
            path=str(project_root / "vector_db")
        )

        self.collection_name = collection_name

        self.collection = self.client.get_or_create_collection(
            name=self.collection_name
        )

    def add_documents(self, ids, documents, embeddings, metadatas):

        self.collection.add(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas
        )

    def search(self, embedding, n_results=5):

        results = self.collection.query(
            query_embeddings=[embedding],
            n_results=n_results
        )

        return results

    def delete_all(self):

        try:
            self.client.delete_collection(
                self.collection_name
            )
        except:
            pass

        self.collection = self.client.get_or_create_collection(
            name=self.collection_name
        )