from playwright.sync_api import sync_playwright
import re
import os
import sys
import shlex
import tempfile

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
                print(f"\nTrovato stream: {url}")
                choice = input("Download or Play? D/P: ").strip().lower()

                # Estrazione link video/audio
                video_url = os.popen(f"curl -s {shlex.quote(url)} | awk '/1080/{{getline; print}}'").read().strip()
                audio_url = os.popen(f"curl -s {shlex.quote(url)} | grep 'type=audio' | grep 'ita' | sed 's/.*URI=\"\\(https[^\\\"]*\\)\".*/\\1/'").read().strip()

                print(f"\n🎞️  Video: {video_url}")
                print(f"🎧  Audio: {audio_url}")

                if not video_url or not audio_url:
                    print("❌ Impossibile trovare le URL audio/video dal manifest.")
                    return

                if choice == "d":
                    nome_file = input("Nome file da salvare: ").strip()
                    print("📥 Download avviato con yt-dlp...")
                    os.system(
                        f"yt-dlp -f bestvideo+bestaudio --merge-output-format mp4 "
                        f"--user-agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        f"AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36' "
                        f"--fragment-retries infinite --concurrent-fragments 5 "
                        f"'{url}' -o '{nome_file}.mp4'"
                    )
                else:
                    print("🎬 Stream trovato! Avvio MPV con audio italiano...")

                    cmd = (
                        f"mpv {shlex.quote(video_url)} --external-file={shlex.quote(audio_url)} "
                        f"--aid=1 "  # forza la prima traccia audio come default
                        f"--user-agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                        f"(KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36' "
                        f"--referrer='https://streamingcommunityz.si' "
                        f"--http-header-fields='Origin: https://streamingcommunityz.si' "
                        f"--no-cache --demuxer-lavf-hacks=no --no-terminal"
                    )

                    os.system(cmd)

        page.on("response", handle_response)

        page.goto(url_pagina)
        # Simula clic per avviare il video
        for _ in range(3):
            page.mouse.click(500, 500)
            page.wait_for_load_state('networkidle')

        page.wait_for_load_state('networkidle')
        browser.close()


# Esempio di utilizzo
url_video = sys.argv[1]
nome_file = url_video.replace("https://streamingcommunityz.si/watch/","").replace("?","").replace("=","")
print("Attendi qualche secondo, sto estraendo lo stream..")
estrai_url_playlist(url_video)
