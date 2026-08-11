import json
import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def scarica_eurospin():
    offerte = []
    url = "https://www.eurospin.it/promozioni/"
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            elementi = soup.find_all(["div", "article"], class_=lambda c: c and ("product" in c.lower() or "card" in c.lower() or "promo" in c.lower()))
            
            for item in elementi:
                titolo_el = item.find(["h2", "h3", "h4", "p", "a"], class_=lambda c: c and ("title" in c.lower() or "name" in c.lower())) or item.find(["h2", "h3", "h4"])
                prezzo_el = item.find(class_=lambda c: c and "price" in c.lower())
                
                if titolo_el:
                    titolo = titolo_el.get_text(strip=True)
                    prezzo = prezzo_el.get_text(strip=True) if prezzo_el else "In offerta"
                    if len(titolo) > 2 and "eurospin" not in titolo.lower():
                        offerte.append({"titolo": titolo, "negozio": "Eurospin", "prezzo": prezzo})
                        if len(offerte) >= 10:
                            break
            
            # Backup in caso di struttura diversa
            if not offerte:
                for a in soup.select("a[title]")[:10]:
                    titolo = a.get("title", "").strip() or a.get_text(strip=True)
                    if len(titolo) > 3:
                        offerte.append({"titolo": titolo, "negozio": "Eurospin", "prezzo": "Offerta Volantino"})
    except Exception as e:
        print(f"⚠️ Errore Eurospin: {e}")
    
    return offerte

def scarica_lidl():
    offerte = []
    url = "https://volantinolidl.it/"
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            elementi = soup.find_all(["div", "article"], class_=lambda c: c and ("product" in c.lower() or "item" in c.lower() or "card" in c.lower()))
            
            if not elementi:
                elementi = soup.select("a[title], div.title, .product-title")
                
            for item in elementi:
                titolo = item.get_text(strip=True)
                if titolo and len(titolo) > 3 and "lidl" not in titolo.lower():
                    offerte.append({"titolo": titolo, "negozio": "Lidl", "prezzo": "Offerta Volantino"})
                    if len(offerte) >= 10:
                        break
    except Exception as e:
        print(f"⚠️ Errore Lidl: {e}")
        
    return offerte

def aggiorna_tutto():
    print("🔄 Inizio aggiornamento offerte...")
    
    offerte_eurospin = scarica_eurospin()
    offerte_lidl = scarica_lidl()
    
    tutte_le_offerte = offerte_eurospin + offerte_lidl
    
    # Formattazione per il file offerte.json
    risultato_json = {}
    for idx, offerta in enumerate(tutte_le_offerte, 1):
        risultato_json[f"offerta_{idx}"] = offerta

    # Salva il file JSON
    with open("offerte.json", "w", encoding="utf-8") as f:
        json.dump(risultato_json, f, ensure_ascii=False, indent=2)

    print(f"✅ Ottenute {len(offerte_eurospin)} offerte da Eurospin e {len(offerte_lidl)} da Lidl.")
    print("💾 File offerte.json aggiornato con successo!")

if __name__ == "__main__":
    aggiorna_tutto()
