import os
import pandas as pd
import requests
from datetime import datetime, timedelta

# ---------------------------------------------------------
# 1) Lettura dei Secrets da GitHub Actions
# ---------------------------------------------------------
BOT_TOKEN = os.getenv("BOT_TOKEN")

CHAT_IDS = [
    os.getenv("CHAT_ID_1"),
    os.getenv("CHAT_ID_2")
]

# ---------------------------------------------------------
# 2) Funzione per inviare messaggi Telegram
# ---------------------------------------------------------
def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    for chat_id in CHAT_IDS:
        if chat_id:
            requests.post(url, data={"chat_id": chat_id, "text": text})

# ---------------------------------------------------------
# 3) Carica il CSV
# ---------------------------------------------------------
df = pd.read_csv("reminder.csv")

# Converte la colonna "data" in datetime
df["data"] = pd.to_datetime(df["data"], format="%Y-%m-%d")

today = datetime.now().date()
seven_days = today + timedelta(days=7)
one_day = today + timedelta(days=1)

messages = []

# ---------------------------------------------------------
# 4) Controlla scadenze
# ---------------------------------------------------------
for index, row in df.iterrows():
    titolo = row["titolo"]
    descrizione = row["descrizione"]
    date = row["data"].date()
    ricorrenza = int(row["ricorrenza"])  # giorni

    # 7 giorni prima
    if date == seven_days:
        messages.append(f"⏳ Mancano 7 giorni a: {titolo} ({date})")

    # 1 giorno prima
    if date == one_day:
        messages.append(f"⚠️ Domani: {titolo} ({date})")

    # Oggi
    if date == today:
        messages.append(f"🎉 Oggi: {titolo}! — {descrizione}")

        # Se ricorrenza > 0 → aggiorna la data
        if ricorrenza > 0:
            new_date = date + timedelta(days=ricorrenza)
            df.at[index, "data"] = new_date

# ---------------------------------------------------------
# 5) Invia i messaggi
# ---------------------------------------------------------
if messages:
    final_message = "📅 Promemoria giornaliero\n\n" + "\n".join(messages)
    send_message(final_message)
else:
    send_message("📭 Nessun promemoria per oggi.")

# ---------------------------------------------------------
# 6) Salva il CSV aggiornato
# ---------------------------------------------------------
df["data"] = df["data"].dt.strftime("%Y-%m-%d")
df.to_csv("reminder.csv", index=False)
