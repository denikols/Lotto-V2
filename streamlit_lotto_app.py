
import streamlit as st
import pandas as pd
from collections import Counter
from datetime import timedelta

st.set_page_config(page_title="Sistema Lotto", layout="centered")
st.title("🎯 Sistema Lotto - Numeri Consigliati e Ripetizioni")

uploaded_file = st.file_uploader("Carica il file CSV delle estrazioni", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file, skiprows=3)
    df["Data"] = pd.to_datetime(df["Data"], errors="coerce")

    ruote = ["Bari", "Cagliari", "Firenze", "Genova", "Milano",
             "Napoli", "Palermo", "Roma", "Torino", "Venezia", "Nazionale"]

    st.success("File caricato correttamente!")

    col1, col2 = st.columns(2)
    with col1:
        ruota = st.selectbox("Scegli la ruota", ruote)
    with col2:
        data_estrazione = st.date_input("Data estrazione", value=df["Data"].max().date())

    n_giocare = st.slider("Quanti numeri vuoi giocare?", min_value=5, max_value=15, value=10)

    def get_numeri_estrazione(data, ruota):
        row = df[df["Data"] == pd.Timestamp(data)]
        if row.empty:
            return []
        cols = [ruota, f"{ruota}.1", f"{ruota}.2", f"{ruota}.3", f"{ruota}.4"]
        numeri = row[cols].iloc[0].tolist()
        return [int(n) for n in numeri if pd.notnull(n)]

    def get_gruppo_numeri(numeri):
        gruppo = set()
        for num in numeri:
            gruppo.update([num, num-1 if num > 1 else 90, num+1 if num < 90 else 1])
        return sorted(gruppo)

    def analizza_successivi(data, ruota):
        prossime = df[df["Data"] > pd.Timestamp(data)].head(5)
        trovati = []
        righe = []
        for i, (_, row) in enumerate(prossime.iterrows(), start=1):
            estratti = [row[f"{ruota}"], row[f"{ruota}.1"], row[f"{ruota}.2"], row[f"{ruota}.3"], row[f"{ruota}.4"]]
            estratti = [int(n) for n in estratti if pd.notnull(n)]
            righe.append({"Estrazione n.": i, "Data": row["Data"].date(), "Numeri usciti": estratti})
            trovati.extend(estratti)
        return trovati, righe

    if st.button("🎲 Calcola numeri da giocare"):
        numeri_base = get_numeri_estrazione(data_estrazione, ruota)
        if not numeri_base:
            st.error("⚠️ Nessun numero trovato per quella data.")
        else:
            gruppo = get_gruppo_numeri(numeri_base)
            trovati, dettaglio_righe = analizza_successivi(data_estrazione, ruota)

            rendimento = Counter()
            for num in gruppo:
                if num in trovati:
                    rendimento[num] += 1

            migliori = sorted(gruppo, key=lambda x: rendimento[x], reverse=True)[:n_giocare]

            st.markdown("### 📌 Numeri consigliati da giocare:")
            st.success(", ".join(map(str, migliori)))

            st.markdown("### 🔁 Ripetizioni nei 5 turni successivi")
            for riga in dettaglio_righe:
                ripetuti = set(riga["Numeri usciti"]) & set(gruppo)
                st.write(f"🗓️ {riga['Data']} → Usciti: {riga['Numeri usciti']} — Ripetuti: {sorted(ripetuti)}")
