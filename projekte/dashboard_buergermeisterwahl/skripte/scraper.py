import requests
from bs4 import BeautifulSoup
import pandas as pd
import time  # Importiere time Modul für Pausen zwischen den Anfragen
import os

# Basis-URL für Wahlbezirke
base_url = "https://wahlergebnisse.brandenburg.de/730572572/1/20250406/buergermeisterwahl_gemeinde/ergebnisse_stimmbezirk_12073057257200{0}.html"

# Liste für alle Daten
all_data = []

# Funktion zum Abrufen der Wahlbezirksdaten
def get_stimmbezirk_data(stimmbezirk_id):
    is_gesamt = len(stimmbezirk_id) != 2
    if is_gesamt:
        url = "https://wahlergebnisse.brandenburg.de/730572572/1/20250406/buergermeisterwahl_gemeinde/ergebnisse.html"
    else:
        url = base_url.format(stimmbezirk_id)  # Ersetze <xx> mit der Zahl (z.B. 01, 02, ..., 27)
    
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Wähle die <tbody> Tabelle mit den Daten
    tbody = soup.find('tbody')
    rows = tbody.find_all('tr')
    
    # Daten für jeden Kandidaten extrahieren
    data = []
    for row in rows:
        cols = row.find_all('td')
        if len(cols) > 1:
            name = row.find_all('th')[1].text.strip()  # Kandidatenname
            stimmen = cols[1].text.strip().replace(".", "")  # Gesamtstimmen
            anteil = cols[0].text.strip()  # Anteil in Prozent
            data.append([name, stimmen, anteil, f"{stimmbezirk_id if not is_gesamt else "gesamt"}"])
    
    return data

# Abrufen der Daten für alle Wahlbezirke
for stimmbezirk_id in range(1, 28):
    formated_id = str(stimmbezirk_id).zfill(2)
    data = get_stimmbezirk_data(formated_id)
    all_data.extend(data)
    
    # Füge eine Wartezeit von 2 Sekunden zwischen den Requests ein, um eine Sperrung der IP zu vermeiden
    time.sleep(2)  # 2 Sekunden warten

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