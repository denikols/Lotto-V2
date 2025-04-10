
import streamlit as st
import pandas as pd
from collections import Counter
from datetime import timedelta
from fpdf import FPDF
import base64

st.set_page_config(page_title="Sistema Lotto", layout="centered")

st.title("🎯 Sistema Lotto - Selezione dei Numeri Migliori")

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
        numeri = [int(n) for n in numeri if pd.notnull(n)]
        return numeri

    def get_gruppo_numeri(numeri):
        gruppo = set()
        for num in numeri:
            gruppo.update([num, num-1 if num > 1 else 90, num+1 if num < 90 else 1])
        return sorted(gruppo)

    def analizza_successivi(data, ruota):
        prossime = df[df["Data"] > data].head(5)
        trovati = []
        for _, row in prossime.iterrows():
            numeri_estratti = [row[f"{ruota}"], row[f"{ruota}.1"], row[f"{ruota}.2"], row[f"{ruota}.3"], row[f"{ruota}.4"]]
            numeri_estratti = [int(n) for n in numeri_estratti if pd.notnull(n)]
            trovati.extend(numeri_estratti)
        return trovati

    def genera_pdf(data, ruota, numeri):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=16)
        pdf.cell(200, 10, txt="Sistema Lotto - Numeri Consigliati", ln=True, align="C")
        pdf.set_font("Arial", size=12)
        pdf.ln(10)
        pdf.cell(200, 10, txt=f"Data: {data}", ln=True)
        pdf.cell(200, 10, txt=f"Ruota: {ruota}", ln=True)
        pdf.cell(200, 10, txt=f"Numeri consigliati: {', '.join(map(str, numeri))}", ln=True)
        return pdf.output(dest="S").encode("latin1")

    if st.button("🎲 Calcola numeri da giocare"):
        numeri_base = get_numeri_estrazione(data_estrazione, ruota)
        if not numeri_base:
            st.error("⚠️ Nessun numero trovato per quella data.")
        else:
            gruppo = get_gruppo_numeri(numeri_base)
            ultime_100 = df.sort_values("Data", ascending=False).head(100)

            rendimento = Counter()
            for data in ultime_100["Data"]:
                trovati = analizza_successivi(data, ruota)
                for num in gruppo:
                    if num in trovati:
                        rendimento[num] += 1

            migliori = sorted(gruppo, key=lambda x: rendimento[x], reverse=True)[:n_giocare]

            st.markdown("### 📌 Numeri consigliati da giocare:")
            st.success(", ".join(map(str, migliori)))

            # Genera PDF
            pdf_bytes = genera_pdf(data_estrazione, ruota, migliori)
            b64 = base64.b64encode(pdf_bytes).decode()
            href = f'<a href="data:application/pdf;base64,{b64}" download="numeri_consigliati.pdf">📄 Scarica PDF con i numeri</a>'
            st.markdown(href, unsafe_allow_html=True)
