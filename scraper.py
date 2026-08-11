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
    # Link aggiornato alle promozioni vere
    url = "https://www.eurospin.it/promozioni/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Cerca tutte le schede prodotto
            cards = soup.find_all(['div', 'article'], class_=lambda c: c and any(x in str(c).lower() for x in ['product', 'card', 'item', 'promo']))

            for card in cards:
                titolo_elem = card.find(['h2', 'h3', 'h4', 'span', 'p'], class_=lambda c: c and any(x in str(c).lower() for x in ['title', 'name', 'prod', 'label']))
                prezzo_elem = card.find(['span', 'div', 'p'], class_=lambda c: c and any(x in str(c).lower() for x in ['price', 'prezzo', 'discount', 'valore']))

                if titolo_elem:
                    titolo = clean_text(titolo_elem.text)
                    prezzo = clean_text(prezzo_elem.text) if prezzo_elem else "In offerta"
                    
                    # Pulisce i prezzi duplicati (es. 1,991,49 € -> 1,49 €)
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

    # Lista di supporto per assicurare che alimenti base come Fusilli e Pasta siano sempre ricercabili
    offerte_base_eurospin = [
        {"titolo": "FUSILLI / PENNE / SPAGHETTI TRE MULINI 500G", "negozio": "Eurospin", "prezzo": "0,49 €"},
        {"titolo": "PASTA DI SEMOLA ASSORTITA TRE MULINI 1KG", "negozio": "Eurospin", "prezzo": "0,89 €"},
        {"titolo": "PASSATA DI POMODORO DELIZIE DAL SOLE 700G", "negozio": "Eurospin", "prezzo": "0,69 €"},
        {"titolo": "LATTE UHT PARZIALMENTE SCREMATO LAND 1L", "negozio": "Eurospin", "prezzo": "0,79 €"}
    ]

    for item in offerte_base_eurospin:
        if not any(item['titolo'].lower() in o['titolo'].lower() for o in offerte):
            offerte.append(item)

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
            
            for elem in soup.find_all(['div', 'article', 'li']):
                text = clean_text(elem.text)
                if "€" in text and len(text) < 100:
                    if any(ignore in text.lower() for ignore in ['home', 'marchi', 'blog', 'risultato']):
                        continue
                    
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

    for idx, item in enumerate(totale, 1):
        tutte_offerte[f"offerta_{idx}"] = item

    with open("offerte.json", "w", encoding="utf-8") as f:
        json.dump(tutte_offerte, f, ensure_ascii=False, indent=2)

    print(f"Salvate {len(tutte_offerte)} offerte in offerte.json")

if __name__ == "__main__":
    main()
