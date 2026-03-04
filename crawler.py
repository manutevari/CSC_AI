import requests
from bs4 import BeautifulSoup

def crawl_url(url):

    try:

        page = requests.get(url)

        soup = BeautifulSoup(page.text,"html.parser")

        return soup.get_text()

    except:

        return ""
