import json

def aggiorna_offerte():
    # Elenco delle offerte (puoi aggiungere tutti i prodotti che vuoi!)
    offerte = {
        "pane": {"negozio": "Conad", "sconto": "1.10€/kg"},
        "latte": {"negozio": "Coop", "sconto": "-25%"},
        "caffè": {"negozio": "Esselunga", "sconto": "2.99€"},
        "caffe": {"negozio": "Esselunga", "sconto": "2.99€"},
        "pasta": {"negozio": "Eurospin", "sconto": "0.55€"},
        "uova": {"negozio": "Lidl", "sconto": "1.20€"},
        "biscotti": {"negozio": "MD", "sconto": "-30%"},
        "nutella": {"negozio": "Decò", "sconto": "3.50€"}
    }

    # Crea/aggiorna automaticamente il file offerte.json
    with open("offerte.json", "w", encoding="utf-8") as f:
        json.dump(offerte, f, ensure_ascii=False, indent=2)
        
    print("✅ File offerte.json generato con successo nella tua cartella!")

if __name__ == "__main__":
    aggiorna_offerte()