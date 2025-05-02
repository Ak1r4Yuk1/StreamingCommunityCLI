import requests
import sqlite3
import os
import json
import sys
from colorama import init, Fore, Back, Style

# Inizializzazione colorama
init(autoreset=True)

# Crea o collega il database temporaneo
conn = sqlite3.connect(':memory:')  # Usa ':memory:' per non creare file su disco
cursor = conn.cursor()

# Crea la tabella
cursor.execute(''' 
CREATE TABLE titoli (
    id INTEGER PRIMARY KEY,
    name TEXT,
    slug TEXT,
    seasons_count INTEGER
)
''')

# Chiedi cosa cercare
ricerca = input(f"{Fore.CYAN}Inserisci il titolo: {Style.RESET_ALL}")

search_title = f'https://streamingcommunity.spa/api/search?q={ricerca}'

r = requests.get(search_title)
data = r.json()

# Cicliamo sui risultati
for item in data["data"]:
    print(f"{Fore.YELLOW}ID:{Style.BRIGHT} {item['id']} , {Fore.GREEN}Nome:{Style.BRIGHT} {item['name']}, {Fore.MAGENTA}Stagioni:{Style.BRIGHT} {item['seasons_count']}")
    link_titolo = f"https://streamingcommunity.spa/titles/{item['id']}-{item['slug']}"
    print(f"{Fore.CYAN}Link:{Style.BRIGHT} {link_titolo}\n")

    # Inseriamo nel database
    cursor.execute('INSERT INTO titoli (id, name, slug, seasons_count) VALUES (?, ?, ?, ?)',
                   (item['id'], item['name'], item['slug'], item['seasons_count']))

conn.commit()

# Ora chiedi all'utente l'ID
id_titolo = input(f"{Fore.CYAN}\nInserisci ID del titolo corrispondente: {Style.RESET_ALL}")

# Recupera informazioni da SQLite
cursor.execute('SELECT id, name, slug, seasons_count FROM titoli WHERE id = ?', (id_titolo,))
titolo = cursor.fetchone()

if titolo:
    id_sel, nome_sel, slug_sel, stagioni_sel = titolo
    print(f"\n{Fore.GREEN}Hai selezionato:{Style.BRIGHT} {nome_sel} ({stagioni_sel} stagioni disponibili)")

    stagione_sel = input(f"{Fore.CYAN}Quale stagione vuoi vedere?: {Style.RESET_ALL}")

    # Costruisci il link per la stagione selezionata
    stagione_link = f"https://streamingcommunity.spa/titles/{id_sel}-{slug_sel}/stagione-{stagione_sel}"
    print(f"{Fore.CYAN}Link alla stagione selezionata:{Style.BRIGHT} {stagione_link}\n")

    headers = {
        "content-type": "application/json",
        "referer": stagione_link,
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36 Edg/135.0.0.0",
        "x-inertia": "true",
        "x-inertia-partial-component": "Titles/Title",
        "x-inertia-partial-data": "loadedSeason,flash",
        "x-inertia-version": "4be520a1c8d10f3e6cbdc91d9d024eda",
        "x-requested-with": "XMLHttpRequest"
    }
    r = requests.get(stagione_link, headers=headers)

    try:
        season_data = r.json()
    except Exception as e:
        print(f"{Fore.RED}Errore parsing JSON stagione:{Style.BRIGHT} {e}")
        print(r.text[:1000])
        sys.exit(1)

    # STAMPA EPISODI + LINK
    try:
        # Parte di codice per chiedere all'utente quale episodio vuole guardare
        stagione_numero = season_data["props"]["loadedSeason"]["number"]
        titolo_id = season_data["props"]["loadedSeason"]["title_id"]
        episodi = season_data["props"]["loadedSeason"]["episodes"]

        print(f"\n{Fore.YELLOW}Episodi trovati per la stagione {stagione_numero}:\n{Style.BRIGHT}")
        for ep in episodi:
            ep_num = ep["number"]
            ep_id = ep["id"]
            ep_plot = ep["plot"]
            print(f"{Fore.GREEN}Stagione {stagione_numero}, Episodio {ep_num}")
            print(f"{Fore.CYAN}Trama: {ep_plot}")
            print(f"{Fore.CYAN}https://streamingcommunity.spa/watch/{titolo_id}?e={ep_id}\n")

        # Chiedi all'utente quale episodio vuole vedere
        episodio_scelto = int(input(f"{Fore.CYAN}Inserisci il numero dell'episodio che vuoi guardare: {Style.RESET_ALL}"))

        # Trova il link dell'episodio scelto
        url_episodio = None
        for ep in episodi:
            if ep["number"] == episodio_scelto:
                ep_id = ep["id"]
                url_episodio = f"https://streamingcommunity.spa/watch/{titolo_id}?e={ep_id}"
                break

        if url_episodio:
            print(f"\n{Fore.GREEN}Ecco il link per l'episodio scelto:{Style.BRIGHT} {url_episodio}")
            # Chiamare il secondo script per avviare l'episodio
            from subprocess import run
            run([sys.executable, 'extract.py', url_episodio])  # Passa il link allo script che avvia il video
        else:
            print(f"{Fore.RED}Episodio non trovato!{Style.RESET_ALL}")

    except Exception as e:
        print(f"{Fore.RED}Errore durante l'estrazione degli episodi:{Style.BRIGHT} {e}")

else:
    print(f"{Fore.RED}Titolo non trovato!{Style.RESET_ALL}")

# Chiudi il database alla fine
conn.close()
