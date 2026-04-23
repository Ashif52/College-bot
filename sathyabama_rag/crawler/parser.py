from bs4 import BeautifulSoup


def extract_text(html):

    soup = BeautifulSoup(html, "html.parser")

    for script in soup(["script", "style"]):
        script.extract()

    text = soup.get_text(" ", strip=True)

    return text