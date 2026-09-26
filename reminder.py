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
df["data"] = pd.to_datetime(df["data"], format="%Y-%m-%d", errors="coerce")

today = datetime.now().date()
seven_days = today + timedelta(days=7)
one_day = today + timedelta(days=1)

messages = []
rows_to_delete = []  # per eliminare i one-shot

# ---------------------------------------------------------
# 4) Funzione per messaggi personalizzati
# ---------------------------------------------------------
def categoria_message(titolo):
    t = titolo.lower()

    if "compleanno" in t:
        return f"🎉 Oggi si festeggia: {titolo}!\nPrepara gli auguri… e magari anche una torta. 🎂😄"

    if "auto" in t:
        return f"🚗 Oggi tocca alla tua auto: {titolo}.\nHai voluto la bicicletta, ora pedala. 😅"

    if "pagare" in t or "rinnovo" in t or "pagamento" in t:
        return f"💸 Oggi scade: {titolo}.\nIl portafoglio piange, ma tu resisti. 😂"

    if "lezione" in t or "corso" in t:
        return f"📚 Oggi hai: {titolo}.\nNiente scuse, si studia! 💪😄"

    if "visita" in t or "medico" in t or "prenotare" in t:
        return f"🏥 Oggi devi: {titolo}.\nLa salute prima di tutto. 😅"

    return f"🔔 Oggi è il giorno di: {titolo}.\nCoraggio, si vola! 💪😄"

# ---------------------------------------------------------
# 5) Controlla scadenze
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
        # Messaggio personalizzato
        messages.append(categoria_message(titolo))

        # Se è one-shot → elimina
        if anni == 0 and mesi == 0 and giorni == 0:
            rows_to_delete.append(index)
        else:
            # Aggiorna la data con ricorrenza
            new_date = date + relativedelta(years=anni, months=mesi, days=giorni)
            df.at[index, "data"] = new_date

# ---------------------------------------------------------
# 6) Elimina i one-shot
# ---------------------------------------------------------
if rows_to_delete:
    df = df.drop(rows_to_delete)

# ---------------------------------------------------------
# 7) Invia i messaggi
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
# 8) Salva il CSV aggiornato
# ---------------------------------------------------------
df["data"] = pd.to_datetime(df["data"], errors="coerce")
df["data"] = df["data"].dt.strftime("%Y-%m-%d")
df.to_csv("reminder.csv", index=False)
