import streamlit as st
import pandas as pd
from collections import Counter
from datetime import timedelta
import base64
import itertools
from itertools import combinations
import numpy as np
from typing import List, Set, Tuple

st.set_page_config(page_title="Sistema Lotto", layout="centered")

st.markdown("""
<style>
@media print {
    .stApp header, .stApp footer, .stSidebar, button, .stToolbar, .stAnnotated, [data-testid="stFileUploadDropzone"] {
        display: none !important;
    }
    body {
        font-size: 12px !important;
    }
    h1, h2, h3 {
        margin-top: 10px !important;
        margin-bottom: 5px !important;
    }
    .element-container, .stAlert, .stDataFrame, .stMarkdown {
        max-width: 100% !important;
        width: 100% !important;
        padding: 0 !important;
        display: block !important;
    }
}
.download-button {
    padding: 0.25rem 0.75rem;
    background-color: #4CAF50;
    color: white !important;
    text-decoration: none;
    border-radius: 4px;
    cursor: pointer;
    display: inline-block;
    margin: 10px 0;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

def create_download_link(content, filename, link_text):
    b64 = base64.b64encode(content.encode()).decode()
    href = f'<a href="data:text/html;charset=utf-8;base64,{b64}" download="{filename}" class="download-button">{link_text}</a>'
    return href

st.title("🎯 Sistema Lotto - Analisi Completa per Ruota con Numeri Spia")

uploaded_file = st.file_uploader("Carica il file CSV delle estrazioni", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file, skiprows=3)
    df["Data"] = pd.to_datetime(df["Data"], errors="coerce")

    ruote = ["Bari", "Cagliari", "Firenze", "Genova", "Milano",
             "Napoli", "Palermo", "Roma", "Torino", "Venezia", "Nazionale"]

    st.success("File caricato correttamente!")

    col1, col2 = st.columns(2)
    with col1:
        ruota_input = st.selectbox("Scegli la ruota per calcolo base", ruote)
    with col2:
        data_estrazione = st.date_input("Data estrazione", value=df["Data"].max().date())

    st.subheader("⚙️ Impostazioni Analisi Numeri Spia")
    numero_spia_input = st.number_input("Inserisci il numero spia da analizzare (1-90)", min_value=1, max_value=90, value=10)
    finestra_analisi_spia = st.slider("Finestra di analisi per numeri spia (ultime N estrazioni)", min_value=50, max_value=1000, value=300, step=50)

    def analizza_numeri_spia(df, numero_spia, ruota, finestra):
        # Seleziona le colonne rilevanti per la ruota specificata
        cols_to_select = [ruota]
        for i in range(1, 5):
            col_name = f"{ruota}.{i}"
            if col_name in df.columns:
                cols_to_select.append(col_name)
        
        # Aggiungi la colonna Data
        cols_to_select.append("Data")
        
        # Filtra il dataframe solo per le colonne selezionate
        df_ruota = df[cols_to_select].dropna()
        df_ruota_sorted = df_ruota.sort_values(by="Data", ascending=False).head(finestra).reset_index(drop=True)

        numeri_successivi = Counter()
        totale_uscite_spia = 0
        
        for i in range(len(df_ruota_sorted) - 1):
            # Converti i numeri dell'estrazione corrente in interi, gestendo gli errori
            estrazione_corrente = []
            for j in range(len(cols_to_select) - 1):  # -1 per escludere la colonna Data
                try:
                    val = df_ruota_sorted.iloc[i, j]
                    if pd.notna(val):  # Controlla se il valore non è NaN
                        estrazione_corrente.append(int(float(val)))
                except (ValueError, TypeError):
                    pass  # Ignora valori non convertibili

            # Converti i numeri dell'estrazione successiva in interi, gestendo gli errori
            estrazione_successiva = []
            for j in range(len(cols_to_select) - 1):  # -1 per escludere la colonna Data
                try:
                    val = df_ruota_sorted.iloc[i + 1, j]
                    if pd.notna(val):  # Controlla se il valore non è NaN
                        estrazione_successiva.append(int(float(val)))
                except (ValueError, TypeError):
                    pass  # Ignora valori non convertibili

            if numero_spia in estrazione_corrente:
                numeri_successivi.update(estrazione_successiva)
                totale_uscite_spia += 1

        if totale_uscite_spia > 0:
            probabilita_successiva = {num: count / totale_uscite_spia for num, count in numeri_successivi.items()}
            probabilita_ordinata = sorted(probabilita_successiva.items(), key=lambda item: item[1], reverse=True)[:5]
            return probabilita_ordinata
        else:
            return []

    st.subheader("🔮 Numeri Suggeriti per i Prossimi Turni (massimo 5)")
    risultati_spia = analizza_numeri_spia(df, numero_spia_input, ruota_input, finestra_analisi_spia)

    if risultati_spia:
        numeri_suggeriti = [f"**{int(num)}** ({probabilita:.2%})" for num, probabilita in risultati_spia]
        st.markdown(f"<p style='font-size:16px; color:green;'>Basati sull'analisi del numero spia <b>{numero_spia_input}</b> sulla ruota di <b>{ruota_input}</b>, i numeri con maggiore probabilità di uscire nei prossimi turni sono: <br> {', '.join(numeri_suggeriti)}</p>", unsafe_allow_html=True)
    else:
        st.info(f"L'analisi del numero spia {numero_spia_input} sulla ruota di {ruota_input} non ha prodotto suggerimenti significativi.")
