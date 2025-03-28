from newspaper import Article
import requests
from bs4 import BeautifulSoup

def process_url(filepath):
    if filepath.lower().startswith('https://') or filepath.lower().startswith('http://'):
        if 'wikipedia.org' in filepath:  # Special case for Wikipedia
            return extract_wikipedia_content(filepath)
        else:
            # Use newspaper3k for other sites
            try:
                article = Article(filepath)
                article.download()
                article.parse()
                return article.text
            except Exception as e:
                return f"Error processing the URL with newspaper3k: {e}"
    else:
        return "Not a URL."

def extract_wikipedia_content(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        content = soup.find('div', {'id': 'bodyContent'})
        return content.get_text() if content else "No content found."
    else:
        return f"Failed to fetch the page. Status code: {response.status_code}"

url = "https://en.wikipedia.org/wiki/Machine_learning"
content = process_url(url)
print(content)
