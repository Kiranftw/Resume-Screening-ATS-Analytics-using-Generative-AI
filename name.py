from newspaper import Article
import requests
from bs4 import BeautifulSoup

def process_url(filepath):
    if filepath.lower().startswith('https://') or filepath.lower().startswith('http://'):

        print("RUNNING NEWSPAPER3K")
        article = Article(filepath)
        article.download()
        article.parse()
        return article.text


url = "https://en.wikipedia.org/wiki/Machine_learning"
content = process_url(url)
print(content)
