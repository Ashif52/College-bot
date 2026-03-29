import requests
import json
import os
from urllib.parse import urljoin
from bs4 import BeautifulSoup

from crawler.filters import valid_url
from crawler.parser import extract_text
from config import BASE_URL, DATA_PATH

visited = set()
pages = []


def crawl(url, depth=0):

    if url in visited:
        return

    visited.add(url)

    print(f"[CRAWLING] {url}")

    try:

        if url.lower().endswith(".pdf"):
            print(f"[DOWNLOADING PDF] {url}")
            # res = requests.get(url, timeout=20)
            # if res.status_code == 200:
            #     filename = url.split("/")[-1].split("?")[0]
            #     os.makedirs("data/pdfs", exist_ok=True)
            #     with open(os.path.join("data/pdfs", filename), "wb") as f:
            #         f.write(res.content)
            # else:
            #     print(f"[SKIP PDF] status {res.status_code} : {url}")
            return

        res = requests.get(url, timeout=10)

        if res.status_code != 200:
            print(f"[SKIP] status {res.status_code} : {url}")
            return

        text = extract_text(res.text)

        pages.append({
            "url": url,
            "content": text
        })

        soup = BeautifulSoup(res.text, "html.parser")

        links = soup.find_all("a")

        print(f"[FOUND {len(links)} LINKS]")

        for link in links:

            href = link.get("href")

            if not href:
                continue

            full = urljoin(BASE_URL, href)

            if BASE_URL in full and valid_url(full):

                crawl(full, depth + 1)

    except Exception as e:

        print("[ERROR]", url, e)


def run():

    print("Starting crawler...")
    print("Base URL:", BASE_URL)

    crawl(BASE_URL)

    print("Total pages scraped:", len(pages))

    with open(DATA_PATH, "w", encoding="utf8") as f:
        json.dump(pages, f, indent=2)

    print("Saved data to:", DATA_PATH)


if __name__ == "__main__":
    run()