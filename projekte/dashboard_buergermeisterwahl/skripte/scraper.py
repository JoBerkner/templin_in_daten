import requests
from bs4 import BeautifulSoup
import pandas as pd
import time  # Importiere time Modul für Pausen zwischen den Anfragen
import os

# Basis-URL für Wahlbezirke
base_url = "https://wahlergebnisse.brandenburg.de/730572572/1/20250406/buergermeisterwahl_gemeinde/ergebnisse_stimmbezirk_00{0}.html"

# Liste für alle Daten
all_data = []

# Funktion zum Abrufen der Wahlbezirksdaten
def get_stimmbezirk_data(stimmbezirk_id):
    is_gesamt = len(stimmbezirk_id) != 2

    data = []
    if is_gesamt:
        url = "https://wahlergebnisse.brandenburg.de/730572572/1/20250406/buergermeisterwahl_gemeinde/ergebnisse.html"

        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        maincontent = soup.find(id="maincontent")
        divs = maincontent.find_all("div", recursive=False) if maincontent else []
        third_div = divs[5] if len(divs) >= 3 else None
    else:
        url = base_url.format(stimmbezirk_id)

        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        maincontent = soup.find(id="maincontent")
        divs = maincontent.find_all("div", recursive=False) if maincontent else []

        third_div = divs[2] if len(divs) >= 3 else None

    if third_div is None:
        expected_candidates = [
            "Bork, Christian", 
            "Beyer, Gordon", 
            "Hennig, Stefan", 
            "Hartphiel, Christian", 
            "Wolk, Andreas", 
            "Lambrecht-Süßenbach, Cornelia"
        ]
        data_dict = {
            name: {"Stimmen": "0", "Anteil": "0"} for name in expected_candidates
        }
        for name in expected_candidates:
            row = [
                name,
                data_dict[name]["Stimmen"],
                data_dict[name]["Anteil"],
                f"{stimmbezirk_id if not is_gesamt else 'gesamt'}"
            ]
            data.append(row)
        
        return data

    tbody = third_div.find('tbody')
    if not tbody:
        print(f"⚠️ Kein <tbody> gefunden für Wahlbezirk {stimmbezirk_id} – vermutlich noch keine Daten vorhanden.")
        return []  # Leere Liste zurückgeben, wenn noch nichts da ist

    rows = tbody.find_all('tr')

    for row in rows:
        cols = row.find_all('td')
        if len(cols) > 1:
            ths = row.find_all('th')
            name = ths[1].text.strip() if len(ths) > 1 else "Unbekannt"
            anteil = cols[1].text.strip().replace(".", "")
            stimmen = cols[0].text.strip()
            data.append([name, stimmen, anteil, f"{stimmbezirk_id if not is_gesamt else 'gesamt'}"])
    return data

# Abrufen der Daten für alle Wahlbezirke
for stimmbezirk_id in range(1, 28):
    formated_id = str(stimmbezirk_id).zfill(2)
    data = get_stimmbezirk_data(formated_id)
    all_data.extend(data)
    
    # Füge eine Wartezeit von 2 Sekunden zwischen den Requests ein, um eine Sperrung der IP zu vermeiden
    #time.sleep(2)  # 2 Sekunden warten

# Auch die Daten für "gesamt" hinzufügen
gesamt_data = get_stimmbezirk_data("gesamt")
all_data.extend(gesamt_data)

# DataFrame erstellen
columns = ["Kandidat", "Stimmen", "Anteil", "Wahlbezirk"]
df = pd.DataFrame(all_data, columns=columns)

# Pfad für die CSV-Datei definieren (ein Ordner über dem aktuellen Skript, in "daten/")
output_folder = os.path.join(os.path.dirname(os.getcwd()), "daten")
output_file = os.path.join(output_folder, "wahlergebnisse.csv")

# Falls der Ordner nicht existiert, erstelle ihn
os.makedirs(output_folder, exist_ok=True)

# DataFrame als CSV speichern
df.to_csv(output_file, index=False, encoding="utf-8")

print(f"CSV-Datei gespeichert unter: {output_file}")