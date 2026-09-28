from backend.rag.retriever import retriever
from backend.rag.embeddings import embedding_service
from backend.rag.vector_store import VectorStore


package_vector_store = VectorStore(
    collection_name="stanley_packages"
)


def get_context(query):

    context = ""

    try:

        results = retriever.retrieve(query)

        if (

            results

            and "documents" in results

            and results["documents"]

            and len(results["documents"][0]) > 0

        ):

            context = "\n\n".join(

                results["documents"][0]

            )

    except Exception as e:

        print("RAG ERROR:", e)
        context = ""

    return context


def get_package_context(query):

    context = ""

    try:

        embedding = embedding_service.create_embedding(
            query
        )

        results = package_vector_store.search(
            embedding=embedding,
            n_results=10
        )

        if (

            results

            and "documents" in results

            and results["documents"]

            and len(results["documents"][0]) > 0

        ):

            context = "\n\n".join(

                results["documents"][0]

            )

    except Exception as e:

        print("PACKAGE RAG ERROR:", e)
        context = ""

    return context