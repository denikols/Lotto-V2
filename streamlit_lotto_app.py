
import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")
st.title("📅 Visualizzatore Estrazioni Lotto")

uploaded_file = st.file_uploader("Carica il file CSV delle estrazioni", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file, skiprows=3)
    df["Data"] = pd.to_datetime(df["Data"], errors="coerce")
    df = df.dropna(subset=["Data"])
    df = df.sort_values("Data", ascending=False)

    ruote = ["Bari", "Cagliari", "Firenze", "Genova", "Milano",
             "Napoli", "Palermo", "Roma", "Torino", "Venezia", "Nazionale"]

    date_uniche = df["Data"].dt.date.unique()
    data_scelta = st.selectbox("Scegli una data di estrazione", date_uniche)

    estrazione = df[df["Data"].dt.date == data_scelta]

    if estrazione.empty:
        st.warning("Nessuna estrazione trovata.")
    else:
        dati = {}

        for ruota in ruote:
            try:
                numeri = estrazione[[f"{ruota}", f"{ruota}.1", f"{ruota}.2", f"{ruota}.3", f"{ruota}.4"]].values.tolist()[0]
                if len(numeri) == 5:
                    dati[ruota] = numeri
                else:
                    dati[ruota] = [None] * 5
            except:
                dati[ruota] = [None] * 5

        df_tabella = pd.DataFrame(dati, index=["1º", "2º", "3º", "4º", "5º"])

        # Colonne per posizionamento a sinistra
        col1, col2 = st.columns([1, 3])
        with col1:
            st.markdown("### 🎯 Numeri estratti")
            st.dataframe(df_tabella.transpose(), use_container_width=True, height=400)
