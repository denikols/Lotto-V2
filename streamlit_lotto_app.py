
import streamlit as st
import pandas as pd
from collections import Counter

st.title("🎯 Selezione Numeri Centrali (Ripetuti) da Estrazione")

uploaded_file = st.file_uploader("Carica il file CSV delle estrazioni", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file, skiprows=3)
    df["Data"] = pd.to_datetime(df["Data"], errors="coerce")
    df = df.sort_values("Data")

    ruote = ["Bari", "Cagliari", "Firenze", "Genova", "Milano",
             "Napoli", "Palermo", "Roma", "Torino", "Venezia", "Nazionale"]

    ruota = st.selectbox("Scegli la ruota", ruote)
    data_estrazione = st.date_input("Scegli la data dell'estrazione", value=df["Data"].max().date(),
                                    min_value=df["Data"].min().date(), max_value=df["Data"].max().date())

    riga = df[df["Data"] == pd.to_datetime(data_estrazione)]

    if riga.empty:
        st.warning("Nessuna estrazione trovata per la data selezionata.")
    else:
        try:
            estratti = riga[[ruota, f"{ruota}.1", f"{ruota}.2", f"{ruota}.3", f"{ruota}.4"]].iloc[0].tolist()
            estratti = [int(n) for n in estratti if pd.notnull(n)]
        except:
            st.error("Errore nella lettura dei numeri.")
            st.stop()

        successivi = []
        for num in estratti:
            successivi.extend([
                num - 1 if num > 1 else 90,
                num + 1 if num < 90 else 1
            ])

        tutti_numeri = estratti + successivi
        conteggi = Counter(tutti_numeri)

        numeri_centrali = [num for num, count in conteggi.items() if count > 1]

        st.markdown("### 🔢 Numeri centrali selezionati (ripetuti)")
        st.write(sorted(numeri_centrali))

        st.markdown("### 📄 Dettaglio conteggi")
        df_conteggi = pd.DataFrame.from_dict(conteggi, orient="index", columns=["Occorrenze"]).sort_index()
        st.dataframe(df_conteggi)
