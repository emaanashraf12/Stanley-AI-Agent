class TextChunker:

    def chunk(self, text, chunk_size=800, overlap=150):

        chunks = []

        start = 0

        while start < len(text):

            end = start + chunk_size

            chunk = text[start:end]

            if chunk.strip():
                chunks.append(chunk)

            if end >= len(text):
                break

            start = end - overlap

        return chunks