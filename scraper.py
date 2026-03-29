import requests
from bs4 import BeautifulSoup
from bs4 import XMLParsedAsHTMLWarning
import warnings
warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning) 

from urllib.parse import urljoin
from tqdm import tqdm
import pdfkit
import os

BASE_URL = "https://www.sathyabama.ac.in"

visited = set()
pages = []

def scrape_page(url):
    if url in visited:
        return
    
    try:
        r = requests.get(url, timeout=10)
        visited.add(url)

        soup = BeautifulSoup(r.text, "html.parser")

        # remove scripts/styles
        for s in soup(["script","style","nav","footer"]):
            s.extract()

        text = soup.get_text(separator="\n")

        pages.append({
            "url": url,
            "text": text
        })

        # find new links
        for a in soup.find_all("a", href=True):
            link = urljoin(BASE_URL, a["href"])

            if BASE_URL in link and link not in visited:
                scrape_page(link)

    except Exception as e:
        print("error:", url)


print("Crawling website...")
scrape_page(BASE_URL)

print("Pages collected:", len(pages))

# create HTML
html = "<h1>Sathyabama University Website Content</h1>"

for p in pages:
    html += f"<h2>{p['url']}</h2>"
    html += "<pre>"
    html += p["text"]
    html += "</pre>"

# save html
with open("website_content.html","w",encoding="utf8") as f:
    f.write(html)

# convert to pdf
pdfkit.from_file("website_content.html","sathyabama_full_content.pdf")

print("PDF generated")