from crawler import WebsiteCrawler
from parser import HTMLParser
from chunker import TextChunker


crawler = WebsiteCrawler(
    "https://stanleytour.com",
    max_pages=5
)

pages = crawler.crawl()

parser = HTMLParser()

chunker = TextChunker()

for page in pages:

    text = parser.clean(page["html"])

    chunks = chunker.chunk(text)

    print("=" * 80)

    print(page["url"])

    print()

    print(chunks[0][:500])

    print()

    print("Chunks:", len(chunks))