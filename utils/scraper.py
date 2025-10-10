import requests
from bs4 import BeautifulSoup
import os

BASE_URL = "https://main.sci.gov.in/judgments"
SAVE_DIR = "pdfs"

def fetch_judgment_links():
    res = requests.get(BASE_URL)
    soup = BeautifulSoup(res.text, "html.parser")

    pdf_links = []
    for a in soup.find_all('a', href=True):
        if a['href'].endswith('.pdf'):
            full_url = f"https://main.sci.gov.in{a['href']}"
            pdf_links.append(full_url)
    return pdf_links

def download_pdfs(pdf_links):
    os.makedirs(SAVE_DIR, exist_ok=True)
    for url in pdf_links[:50]:  # limit for now
        name = url.split("/")[-1]
        path = os.path.join(SAVE_DIR, name)

        if not os.path.exists(path):
            print(f"Downloading {name}")
            r = requests.get(url)
            with open(path, 'wb') as f:
                f.write(r.content)

if __name__ == "__main__":
    links = fetch_judgment_links()
    download_pdfs(links)