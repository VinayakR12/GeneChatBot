from bs4 import BeautifulSoup
import requests

def fetch_genecards_summary(gene_symbol):
    url = f"https://www.genecards.org/cgi-bin/carddisp.pl?gene={gene_symbol}"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    summary = soup.find('div', {'class': 'gc-subsection-content'})
    return summary.text.strip() if summary else "No summary found."
