import os
import pandas as pd
import requests
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

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
df["data"] = pd.to_datetime(df["data"], format="%Y-%m-%d", errors="coerce")

today = datetime.now().date()
seven_days = today + timedelta(days=7)
one_day = today + timedelta(days=1)

messages = []

# ---------------------------------------------------------
# 4) Controlla scadenze
# ---------------------------------------------------------
for index, row in df.iterrows():
    titolo = row["titolo"]
    date = row["data"].date()

    anni = int(row["anni"])
    mesi = int(row["mesi"])
    giorni = int(row["giorni"])

    # 7 giorni prima
    if date == seven_days:
        messages.append(
            f"⏳ Fra 7 giorni scade “{titolo}”.\n"
            f"Hai una settimana per convincerti che non puoi rimandare ancora. 😅 ({date})"
        )

    # 1 giorno prima
    if date == one_day:
        messages.append(
            f"⚠️ Domani tocca a “{titolo}”.\n"
            f"Non fare finta di niente, ti ho visto. 👀 ({date})"
        )

    # Oggi
    if date == today:
        messages.append(
            f"🎉 Oggi è il grande giorno: {titolo}!\n"
            f"Coraggio, ce la puoi fare. 💪😂"
        )

        # Aggiorna la data con anni/mesi/giorni
        new_date = date + relativedelta(years=anni, months=mesi, days=giorni)
        df.at[index, "data"] = new_date

# ---------------------------------------------------------
# 5) Invia i messaggi
# ---------------------------------------------------------
if messages:
    final_message = "📅 Promemoria giornaliero\n\n" + "\n\n".join(messages)
    send_message(final_message)
else:
    send_message(
        "📭 Nessun promemoria per oggi.\n"
        "Goditi la pace prima della tempesta. 😎"
    )

# ---------------------------------------------------------
# 6) Salva il CSV aggiornato
# ---------------------------------------------------------
df["data"] = pd.to_datetime(df["data"], errors="coerce")
df["data"] = df["data"].dt.strftime("%Y-%m-%d")
df.to_csv("reminder.csv", index=False)
