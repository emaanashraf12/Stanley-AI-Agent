from backend.rag.vector_store import VectorStore
from backend.rag.embeddings import embedding_service


class Retriever:

    def __init__(self):
        self.vector_store = VectorStore()

    def retrieve(self, question, n_results=10):

        embedding = embedding_service.create_embedding(question)

        results = self.vector_store.search(
            embedding=embedding,
            n_results=n_results
        )

        return results


retriever = Retriever()