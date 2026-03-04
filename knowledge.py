import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

from database import conn
from embeddings import chunk, store_vector


def smart_crawl(start_url, max_pages=20):

    visited = set()
    queue = [start_url]

    domain = urlparse(start_url).netloc

    while queue and len(visited) < max_pages:

        url = queue.pop(0)

        if url in visited:
            continue

        visited.add(url)

        try:

            r = requests.get(url, timeout=10)

            soup = BeautifulSoup(r.text, "lxml")

            for t in soup(["script", "style", "noscript"]):
                t.extract()

            text = soup.get_text(" ")

            for c in chunk(text):

                store_vector(c, url)

            for link in soup.find_all("a", href=True):

                absolute = urljoin(url, link["href"])

                if domain in absolute and absolute not in visited:

                    queue.append(absolute)

        except Exception:

            pass

    conn.commit()
