import requests
from bs4 import BeautifulSoup


def crawl_website(url):

    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")

    text = soup.get_text()

    return text
