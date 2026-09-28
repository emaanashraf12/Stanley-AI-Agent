import uuid

from backend.rag.crawler import WebsiteCrawler
from backend.rag.parser import HTMLParser
from backend.rag.chunker import TextChunker
from backend.rag.embeddings import embedding_service
from backend.rag.vector_store import VectorStore


crawler = WebsiteCrawler(
    "https://stanleytour.com",
    max_pages=None
)

parser = HTMLParser()

chunker = TextChunker()

vector_store = VectorStore()

package_vector_store = VectorStore(
    collection_name="stanley_packages"
)

vector_store.delete_all()

package_vector_store.delete_all()

pages = crawler.crawl()

total_chunks = 0
indexed_pages = 0

package_chunks = 0
package_pages = 0


for page in pages:

    text = parser.clean(
        page["html"]
    )

    if not text or not text.strip():

        print(
            "Skipped empty page:",
            page["url"]
        )

        continue

    chunks = chunker.chunk(
        text
    )

    if not chunks:

        print(
            "No chunks created:",
            page["url"]
        )

        continue

    print(
        "Indexing:",
        page["url"],
        "| Chunks:",
        len(chunks)
    )

    indexed_pages += 1

    is_package_page = (
        "/package/" in page["url"]
    )

    if is_package_page:

        package_pages += 1

    for chunk in chunks:

        if not chunk.strip():
            continue

        embedding = (
            embedding_service.create_embedding(
                chunk
            )
        )

        document_id = str(
            uuid.uuid4()
        )

        metadata = {
            "url": page["url"]
        }

        vector_store.add_documents(
            ids=[
                document_id
            ],
            documents=[
                chunk
            ],
            embeddings=[
                embedding
            ],
            metadatas=[
                metadata
            ]
        )

        total_chunks += 1

        if is_package_page:

            package_vector_store.add_documents(
                ids=[
                    str(uuid.uuid4())
                ],
                documents=[
                    chunk
                ],
                embeddings=[
                    embedding
                ],
                metadatas=[
                    metadata
                ]
            )

            package_chunks += 1


print()
print(
    "=========================================="
)
print(
    "KNOWLEDGE BASE CREATED SUCCESSFULLY"
)
print(
    "=========================================="
)
print(
    "Pages discovered:",
    len(pages)
)
print(
    "Pages indexed:",
    indexed_pages
)
print(
    "Chunks indexed:",
    total_chunks
)
print(
    "Package pages indexed:",
    package_pages
)
print(
    "Package chunks indexed:",
    package_chunks
)
print(
    "=========================================="
)