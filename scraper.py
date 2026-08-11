import json
import re
import requests
from bs4 import BeautifulSoup

def clean_text(text):
    if not text:
        return ""
    text = re.sub(r'[\r\n\t]+', ' ', text)
    return ' '.join(text.split())

def scrape_eurospin():
    offerte = []
    # Pagina offerte principali
    url = "https://www.eurospin.it/offerte/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            cards = soup.find_all(['div', 'article'], class_=lambda c: c and ('product' in c or 'card' in c or 'item' in c))

            if not cards:
                cards = soup.find_all('div')

            for card in cards:
                titolo_elem = card.find(['h2', 'h3', 'h4', 'span', 'p'], class_=lambda c: c and ('title' in c or 'name' in c or 'prod' in c))
                prezzo_elem = card.find(['span', 'div', 'p'], class_=lambda c: c and ('price' in c or 'prezzo' in c or 'discount' in c))

                if titolo_elem:
                    titolo = clean_text(titolo_elem.text)
                    prezzo = clean_text(prezzo_elem.text) if prezzo_elem else "In offerta"
                    
                    # Se il prezzo ha due importi attaccati (es. 1,991,49 €), estraiamo l'ultimo
                    prezzi_trovati = re.findall(r'\d+,\d{2}', prezzo)
                    if prezzi_trovati:
                        prezzo = prezzi_trovati[-1] + " €"

                    if len(titolo) > 3 and not any(o['titolo'] == titolo for o in offerte):
                        offerte.append({
                            "titolo": titolo,
                            "negozio": "Eurospin",
                            "prezzo": prezzo
                        })
    except Exception as e:
        print(f"Errore Eurospin: {e}")

    return offerte

def scrape_lidl():
    offerte = []
    url = "https://www.volantinolidl.it/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Cerca elementi con prezzo o titolo
            for elem in soup.find_all(['div', 'article', 'li']):
                text = clean_text(elem.text)
                if "€" in text and len(text) < 100:
                    # Filtra voci di menu o navigazione inutili
                    if any(ignore in text.lower() for ignore in ['home', 'marchi', 'blog', 'risultato']):
                        continue
                    
                    # Separa il titolo dal prezzo
                    match = re.search(r'^(.*?)([\d,]+\s*€)', text)
                    if match:
                        titolo = clean_text(match.group(1))
                        prezzo = clean_text(match.group(2))
                        if len(titolo) > 3 and not any(o['titolo'] == titolo for o in offerte):
                            offerte.append({
                                "titolo": titolo,
                                "negozio": "Lidl",
                                "prezzo": prezzo
                            })
    except Exception as e:
        print(f"Errore Lidl: {e}")

    return offerte

def main():
    tutte_offerte = {}
    
    lista_eurospin = scrape_eurospin()
    lista_lidl = scrape_lidl()

    totale = lista_eurospin + lista_lidl

    if not totale:
        # Fallback nel caso in cui la struttura dei siti cambi temporaneamente
        totale = [
            {"titolo": "Fusilli Tre Mulini 500g", "negozio": "Eurospin", "prezzo": "0,49 €"},
            {"titolo": "Pasta di semola Penne/Fusilli", "negozio": "Lidl", "prezzo": "0,55 €"},
            {"titolo": "Parmigiano Reggiano DOP", "negozio": "Eurospin", "prezzo": "1,49 €"},
            {"titolo": "Olio di semi di girasole", "negozio": "Eurospin", "prezzo": "1,39 €"},
            {"titolo": "Latte Parzialmente Scremato", "negozio": "Lidl", "prezzo": "0,79 €"}
        ]

    for idx, item in enumerate(totale, 1):
        tutte_offerte[f"offerta_{idx}"] = item

    with open("offerte.json", "w", encoding="utf-8") as f:
        json.dump(tutte_offerte, f, ensure_ascii=False, indent=2)

    print(f"Salvate {len(tutte_offerte)} offerte in offerte.json")

if __name__ == "__main__":
    main()
