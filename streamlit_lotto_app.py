# streamlit_app.py
import streamlit as st
import pandas as pd
from datetime import timedelta

st.title("Caricamento Dati e Impostazioni")

uploaded_file = st.file_uploader("Carica il file CSV delle estrazioni", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file, skiprows=3)
    df["Data"] = pd.to_datetime(df["Data"], errors="coerce")
    st.session_state['df'] = df

    ruote = ["Bari", "Cagliari", "Firenze", "Genova", "Milano",
             "Napoli", "Palermo", "Roma", "Torino", "Venezia", "Nazionale"]
    ruota_input = st.selectbox("Scegli la ruota per calcolo base", ruote, key="ruota_input")
    data_estrazione = st.date_input("Data estrazione", value=df["Data"].max().date(), key="data_estrazione")
    st.session_state['ruota_input'] = ruota_input
    st.session_state['data_estrazione'] = data_estrazione

    st.subheader("Impostazioni Analisi Numeri Spia")
    numero_spia_input = st.number_input("Inserisci il numero spia da analizzare (1-90)", min_value=1, max_value=90, value=10, key="numero_spia_input")
    finestra_analisi_spia = st.slider("Finestra di analisi per numeri spia (ultime N estrazioni)", min_value=50, max_value=1000, value=300, step=50, key="finestra_analisi_spia")

    st.session_state['dati_iniziali_caricati'] = True

    if st.button("Vai all'Analisi Dettagliata"):
        st.switch_page("pages/2_Analisi_Dettagliata.py")
else:
    st.info("Carica un file CSV per iniziare.")