import subprocess
import json
import os
import time

# Putanja do bas-celik.exe
BAS_CELIK_PATH = r"F:\Daki\GitHub\ENOVA_VENDING_5\bas-celik\bas-celik.exe"
OUTPUT_JSON = r"F:\Daki\GitHub\ENOVA_VENDING_5\licna_karta.json"

print(f"[TEST] Pokrećem: {BAS_CELIK_PATH} -json {OUTPUT_JSON}")

try:
    # Pokreni Baš Čelik sa JSON opcijom
    rezultat = subprocess.run(
        [BAS_CELIK_PATH, "-json", OUTPUT_JSON],
        timeout=20
    )
    print("[TEST] Povratni kod:", rezultat.returncode)

    if rezultat.returncode != 0:
        print("❌ Greška: bas-celik.exe nije uspešno završio.")
        exit()

    # Sačekaj da se fajl pojavi
    time.sleep(1)

    if not os.path.exists(OUTPUT_JSON):
        print("❌ JSON fajl nije napravljen.")
        exit()

    # Učitaj i prikaži podatke
    with open(OUTPUT_JSON, "r", encoding="utf-8") as f:
        podaci = json.load(f)

    print("✅ JSON sadržaj:")
    print(json.dumps(podaci, indent=4, ensure_ascii=False))

except subprocess.TimeoutExpired:
    print("❌ Greška: vreme izvršavanja isteklo (timeout).")
except FileNotFoundError:
    print("❌ Greška: putanja do bas-celik.exe nije tačna.")
except Exception as e:
    print(f"❌ Neočekivana greška: {e}")
