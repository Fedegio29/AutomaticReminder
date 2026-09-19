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
        if chat_id:  # evita errori se un ID è vuoto
            requests.post(url, data={"chat_id": chat_id, "text": text})

# ---------------------------------------------------------
# 3) Carica il CSV
# ---------------------------------------------------------
df = pd.read_csv("reminder.csv")

# Assicura che la colonna date sia datetime
df["date"] = pd.to_datetime(df["date"], format="%d/%m/%Y")

today = datetime.now().date()
seven_days = today + timedelta(days=7)
one_day = today + timedelta(days=1)

messages = []

# ---------------------------------------------------------
# 4) Controlla scadenze
# ---------------------------------------------------------
for index, row in df.iterrows():
    name = row["name"]
    date = row["date"].date()
    recurring = row.get("recurring", "no").lower()

    # 7 giorni prima
    if date == seven_days:
        messages.append(f"⏳ Mancano 7 giorni a: {name} ({date.strftime('%d/%m/%Y')})")

    # 1 giorno prima
    if date == one_day:
        messages.append(f"⚠️ Domani: {name} ({date.strftime('%d/%m/%Y')})")

    # Oggi
    if date == today:
        messages.append(f"🎉 Oggi: {name}!")

        # Se è ricorrente → aggiorna al prossimo anno
        if recurring == "yes":
            new_date = date.replace(year=date.year + 1)
            df.at[index, "date"] = new_date

# ---------------------------------------------------------
# 5) Invia i messaggi
# ---------------------------------------------------------
if messages:
    final_message = "📅 *Promemoria giornaliero*\n\n" + "\n".join(messages)
    send_message(final_message)
else:
    send_message("📭 Nessun promemoria per oggi.")

# ---------------------------------------------------------
# 6) Salva il CSV aggiornato (ricorrenze)
# ---------------------------------------------------------
df["date"] = df["date"].dt.strftime("%d/%m/%Y")
df.to_csv("reminder.csv", index=False)
