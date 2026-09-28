from bs4 import BeautifulSoup


class HTMLParser:

    def clean(self, html):

        soup = BeautifulSoup(html, "lxml")

        for tag in soup(["script", "style", "noscript", "footer", "header"]):
            tag.decompose()

        text = soup.get_text(separator=" ")

        return " ".join(text.split())