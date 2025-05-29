import requests
import sqlite3
import os
import sys
from colorama import init, Fore, Style
from InquirerPy import inquirer


class DevNull:
    def write(self,msg):
        pass

sys.stderr = DevNull()


os.system("cls")
init(autoreset=True)

conn = sqlite3.connect(':memory:')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE titoli (
    id INTEGER PRIMARY KEY,
    name TEXT,
    slug TEXT,
    seasons_count INTEGER
)
''')

ricerca = inquirer.text(message="Inserisci il titolo da cercare:").execute()
os.system("cls")
search_title = f'https://streamingunity.to/api/search?q={ricerca}'

try:
    r = requests.get(search_title)
    data = r.json()
except Exception as e:
    print(f"{Fore.RED}Errore durante la richiesta: Prova ad attivare la VPN in un paese fuori dall'Italia")
    sys.exit(1)

# Inserimento e visualizzazione titoli
scelte = []
for item in data["data"]:
    entry = f"{item['id']} - {item['name']} ({item['seasons_count']} stagioni)"
    scelte.append(entry)
    cursor.execute('INSERT INTO titoli (id, name, slug, seasons_count) VALUES (?, ?, ?, ?)',
                   (item['id'], item['name'], item['slug'], item['seasons_count']))

conn.commit()

# Selezione titolo
scelta_titolo = inquirer.select(message="Scegli un titolo:", choices=scelte).execute()
id_titolo = scelta_titolo.split(" - ")[0]
os.system("cls")
cursor.execute('SELECT id, name, slug, seasons_count FROM titoli WHERE id = ?', (id_titolo,))
titolo = cursor.fetchone()

if not titolo:
    print(f"{Fore.RED}Titolo non trovato!{Style.RESET_ALL}")
    sys.exit(1)

id_sel, nome_sel, slug_sel, stagioni_sel = titolo
print(f"\n{Fore.GREEN}Hai selezionato:{Style.BRIGHT} {nome_sel} ({stagioni_sel} stagioni disponibili)")

stagione_sel = inquirer.select(
    message="Scegli una stagione:",
    choices=[str(i + 1) for i in range(stagioni_sel)]
).execute()

os.system("cls")

stagione_link = f"https://streamingunity.to/it/titles/{id_sel}-{slug_sel}/season-{stagione_sel}"
print(f"{Fore.CYAN}Link alla stagione selezionata:{Style.BRIGHT} {stagione_link}\n")

headers = {
    'accept': 'text/html, application/xhtml+xml',
    'accept-language': 'it,it-IT;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'cache-control': 'no-cache',
    'content-type': 'application/json',
    'pragma': 'no-cache',
    'priority': 'u=1, i',
    'referer': f'{stagione_link}',
    'sec-ch-ua': '"Chromium";v="136", "Microsoft Edge";v="136", "Not.A/Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36 Edg/136.0.0.0',
    'x-inertia': 'true',
    'x-inertia-partial-component': 'Titles/Title',
    'x-inertia-partial-data': 'loadedSeason,flash',
    'x-inertia-version': '51bcd00e70993d1c875cf45033ddaad0',
    'x-requested-with': 'XMLHttpRequest',
    'x-xsrf-token': 'eyJpdiI6IjFMYmh1dUgvUENtSjJGRm81aGdUM2c9PSIsInZhbHVlIjoiZW52YTBZZVQyWXFJVXVVdm94dXVTeVlpUGlTSUlTRkkwQjc2UDJEdnpOMVZhN3lkR2FtT0Q0RW85YmR5OUdqc0IyUHB1blExMEdadkNoWFRKRFM4SnlLd1A3aXF0UmN2RjB1NGlQcllVSlBDcjBQMlhFU0hMYlc0QWE5aTVYcTEiLCJtYWMiOiJjNTQ2N2UyNzk0YWY3YzUxMzA2MGVjMmJkOTRlZDNkY2Y0NjQ4NDEzMjc4ZDY0Mzc2NGQ0ZGUwOTcwNTc3Mzg4IiwidGFnIjoiIn0%3D'
}

try:
    r = requests.get(stagione_link, headers=headers)
    season_data = r.json()
except Exception as e:
    print(f"{Fore.RED}Errore parsing JSON stagione:{Style.BRIGHT} {e}")
    print(r.text[:1000])
    sys.exit(1)

episodi = season_data["props"]["loadedSeason"]["episodes"]
stagione_numero = season_data["props"]["loadedSeason"]["number"]
titolo_id = season_data["props"]["loadedSeason"]["title_id"]

# Menu per episodi
episodi_choices = [
    f"{ep['number']:02d} - {ep['plot']}" for ep in episodi
]

episodio_scelto = inquirer.select(message="Scegli un episodio:", choices=episodi_choices).execute()
numero_ep = int(episodio_scelto.split(" - ")[0])

# Trova link episodio
url_episodio = None
for ep in episodi:
    if ep["number"] == numero_ep:
        ep_id = ep["id"]
        url_episodio = f"https://streamingunity.to/it/watch/{titolo_id}?e={ep_id}"
        break

if url_episodio:
    print(f"\n{Fore.GREEN}Ecco il link per l'episodio scelto:{Style.BRIGHT} {url_episodio}")
    from subprocess import run
    run([sys.executable, 'extract.py', url_episodio])
else:
    print(f"{Fore.RED}Episodio non trovato!{Style.RESET_ALL}")

conn.close()
