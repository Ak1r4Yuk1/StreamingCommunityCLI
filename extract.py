from playwright.sync_api import sync_playwright
import re
import os
import sys

class DevNull:
    def write(self,msg):
        pass

sys.stderr = DevNull()

def estrai_url_playlist(url_pagina):
    user_agent = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/116.0.0.0 Safari/537.36"
    )

    pattern = re.compile(r"https://vixcloud\.co/playlist/\d+\?token=[^&]+&expires=\d+")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            channel="chrome",
            ignore_default_args=["--headless"],
            args=["--headless=new"]
        )
        context = browser.new_context()
        page = context.new_page()

        # Gestione dei popup: chiusura automatica
        context.on("page", lambda popup: popup.close())

        # Intercetta le risposte di rete
        def handle_response(response):
            url = response.url
            if pattern.match(url):
                print(url)
                choise = input("Download or Play? D/P: ")
                if choise == ("P" or "p"):
                    print("Stream trovato! Sto aprendo MPV per riprodurlo")
                    os.system(f"mpv --user-agent=\"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0\" \"{url}\" --no-terminal")
                elif choise == ("D" or "d"):
                    os.system(f"yt-dlp -f bestvideo+bestaudio --merge-output-format mp4 --user-agent=\"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0\" --fragment-retries infinite --concurrent-fragments 5 \"{url}\" -o {nome_file}.mp4")
                else:
                    print("Stream trovato! Sto aprendo MPV per riprodurlo")
                    os.system(f"mpv --user-agent=\"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0\" \"{url}\" --no-terminal")
        page.on("response", handle_response)

        page.goto(url_pagina)
        # Simula clic per avviare il video
        page.mouse.click(500, 500)
        page.wait_for_load_state('networkidle')
        page.mouse.click(500, 500)
        page.wait_for_load_state('networkidle')
        page.mouse.click(500, 500)

        # Attendi per assicurarti che tutte le richieste siano intercettate
        page.wait_for_load_state('networkidle')

        browser.close()

# Esempio di utilizzo
url_video = sys.argv[1]
#  4615e27256
nome_file = url_video.replace("https://streamingcommunityz.si/watch/","").replace("?", "").replace("=","")
print("Attendi qualche secondo, sto estraendo lo stream..")
estrai_url_playlist(url_video)
