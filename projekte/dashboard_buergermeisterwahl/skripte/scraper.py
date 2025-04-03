import requests
import pandas as pd
from bs4 import BeautifulSoup
import os

# URL der Wahlergebnisseite
url = "https://wahlergebnisse.brandenburg.de/730572572/1/20250406/buergermeisterwahl_gemeinde/ergebnisse_gemeinde_120730572572.html"

# HTTP-Anfrage senden und HTML-Inhalt abrufen
response = requests.get(url)
response.raise_for_status()  # Stellt sicher, dass die Anfrage erfolgreich war

# HTML-Inhalt mit BeautifulSoup parsen
soup = BeautifulSoup(response.text, 'html.parser')

# Die Tabelle mit den Wahlergebnissen finden
table = soup.find('table')

# Listen zum Speichern der Daten
kandidaten = []
stimmen = []
anteile = []

# Sicherstellen, dass die Tabelle gefunden wurde
if table:
    tbody = table.find('tbody')
    if tbody:
        for row in tbody.find_all('tr'):
            headers = row.find_all('th')  # Kandidatenname ist im zweiten <th>
            cells = row.find_all('td')  # Anteil und Gesamtstimmen sind in <td>

            if len(headers) > 1 and len(cells) > 1:
                kandidat = headers[1].get_text(strip=True)  # Kandidatenname
                anteil = cells[1].get_text(strip=True)  # Prozentualer Anteil
                stimme = cells[0].get_text(strip=True)  # Gesamtanzahl der Stimmen

                # Daten in Listen speichern
                kandidaten.append(kandidat)
                stimmen.append(stimme)
                anteile.append(anteil)

# DataFrame erstellen
df = pd.DataFrame({
    "Kandidat": kandidaten,
    "Gesamtstimmen": stimmen,
    "Anteil (%)": anteile
})

# Pfad für die CSV-Datei definieren (ein Ordner über dem aktuellen Skript, in "daten/")
output_folder = os.path.join(os.path.dirname(os.getcwd()), "daten")
output_file = os.path.join(output_folder, "wahlergebnisse.csv")

# Falls der Ordner nicht existiert, erstelle ihn
os.makedirs(output_folder, exist_ok=True)

# DataFrame als CSV speichern
df.to_csv(output_file, index=False, encoding="utf-8")

print(f"CSV-Datei gespeichert unter: {output_file}")