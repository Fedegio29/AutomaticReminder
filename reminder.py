import pandas as pd
from datetime import datetime, timedelta
import requests
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def log(msg):
    print(f"[LOG] {msg}")

def send_telegram_message(text):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        params = {"chat_id": CHAT_ID, "text": text}
        r = requests.get(url, params=params)
        log(f"Messaggio inviato. Risposta Telegram: {r.text}")
    except Exception as e:
        log(f"ERRORE nell'invio del messaggio: {e}")

def check_reminders():
    log("=== Avvio script reminder ricorrenti ===")

    if not os.path.exists("reminder.csv"):
        log("ERRORE: reminder.csv NON trovato!")
        return

    df = pd.read_csv("reminder.csv")
    log("Contenuto CSV:")
    log(df)

    today = datetime.now().date()
    log(f"Giorno attuale: {today}")

    updated = False  # per sapere se dobbiamo riscrivere il CSV

    for index, row in df.iterrows():
        log(f"Controllo reminder #{index}: {row['titolo']}")

        try:
            reminder_day = datetime.strptime(row["data"], "%Y-%m-%d").date()
        except Exception as e:
            log(f"ERRORE parsing data '{row['data']}': {e}")
            continue

        ricorrenza = int(row["ricorrenza"])
        log(f"Ricorrenza: ogni {ricorrenza} giorni")

        diff = (reminder_day - today).days
        log(f"Giorni alla scadenza: {diff}")

        # 7 giorni prima
        if diff == 7:
            log("→ Mancano 7 giorni: invio recap")
            msg = (
                f"📅 Promemoria (7 giorni prima)\n"
                f"🔔 {row['titolo']}\n"
                f"{row['descrizione']}\n"
                f"📆 Scadenza: {row['data']}"
            )
            send_telegram_message(msg)

        # 1 giorno prima
        elif diff == 1:
            log("→ Mancano 24 ore: invio recap")
            msg = (
                f"⏳ Promemoria (1 giorno prima)\n"
                f"🔔 {row['titolo']}\n"
                f"{row['descrizione']}\n"
                f"📆 Scadenza: {row['data']}"
            )
            send_telegram_message(msg)

        # Scadenza oggi → aggiorna la data
        elif diff == 0:
            log("→ Scadenza OGGI: invio messaggio e aggiorno la data")

            msg = (
                f"🔔 Scadenza OGGI!\n"
                f"{row['titolo']}\n"
                f"{row['descrizione']}\n"
                f"📆 Scadenza: {row['data']}\n"
                f"🔁 Ricorrenza: ogni {ricorrenza} giorni"
            )
            send_telegram_message(msg)

            # aggiorna la data
            nuova_data = reminder_day + timedelta(days=ricorrenza)
            df.at[index, "data"] = nuova_data.strftime("%Y-%m-%d")
            updated = True
            log(f"Nuova data impostata: {nuova_data}")

        else:
            log("→ Nessun recap da inviare.")

    # Se abbiamo aggiornato il CSV, riscriviamolo
    if updated:
        df.to_csv("reminder.csv", index=False)
        log("CSV aggiornato con le nuove date.")

    log("=== Fine script ===")

if __name__ == "__main__":
    check_reminders()
