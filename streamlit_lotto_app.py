
import streamlit as st
import pandas as pd
from collections import Counter
from datetime import timedelta

st.set_page_config(page_title="Sistema Lotto", layout="centered")
st.title("🎯 Sistema Lotto - Analisi Completa per Ruota")

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
        # Evidenziazione delle date disponibili in rosso
        date_disponibili = df["Data"].dropna().dt.date.unique()
        data_estrazione = st.date_input("Data estrazione", value=df["Data"].max().date())

    st.markdown("#### 📅 Date con estrazioni (evidenziate):", unsafe_allow_html=True)
    st.markdown(
        "<div style='color:red; font-weight:bold'>" +
        ", ".join(sorted({d.strftime("%Y-%m-%d") for d in date_disponibili})) +
        "</div>",
        unsafe_allow_html=True
    )
