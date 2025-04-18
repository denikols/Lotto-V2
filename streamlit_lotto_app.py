
import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")
st.title("📅 Visualizzatore Estrazioni Lotto - Confronto Due Date")

ruote = ["Bari", "Cagliari", "Firenze", "Genova", "Milano",
         "Napoli", "Palermo", "Roma", "Torino", "Venezia", "Nazionale"]

def trova_consecutivi(lista):
    lista_ordinata = sorted([n for n in lista if isinstance(n, int)])
    consecutivi = set()
    for i in range(len(lista_ordinata) - 1):
        if lista_ordinata[i] + 1 == lista_ordinata[i + 1]:
            consecutivi.add(lista_ordinata[i])
            consecutivi.add(lista_ordinata[i + 1])
    return consecutivi

uploaded_file = st.file_uploader("Carica il file CSV delle estrazioni", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file, skiprows=3)
    df["Data"] = pd.to_datetime(df["Data"], errors="coerce")
    df = df.dropna(subset=["Data"])
    df = df.sort_values("Data", ascending=False)
    date_uniche = df["Data"].dt.date.unique()

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🔎 Tabella sinistra")
        data_sx = st.selectbox("Scegli una data (SX)", date_uniche, key="data_sx")
        estrazione_sx = df[df["Data"].dt.date == data_sx]
        dati_sx = {}
        consecutivi_sx = set()

        for ruota in ruote:
            try:
                numeri = estrazione_sx[[f"{ruota}", f"{ruota}.1", f"{ruota}.2", f"{ruota}.3", f"{ruota}.4"]].values.tolist()[0]
                if len(numeri) == 5:
                    dati_sx[ruota] = numeri
                    consecutivi_sx.update(trova_consecutivi(numeri))
                else:
                    dati_sx[ruota] = [None] * 5
            except:
                dati_sx[ruota] = [None] * 5

        df_sx = pd.DataFrame(dati_sx, index=["1º", "2º", "3º", "4º", "5º"]).transpose()

        def style_sx(val):
            if isinstance(val, int) and val in consecutivi_sx:
                return 'color: red; font-weight: bold; font-size: 18px;'
            return ''

        altezza = (len(df_sx) + 1) * 40
        st.dataframe(df_sx.style.applymap(style_sx), use_container_width=False, height=altezza, width=600)

    with col2:
        st.markdown("### 🔎 Tabella destra")
        data_dx = st.selectbox("Scegli una data (DX)", date_uniche, key="data_dx")
        estrazione_dx = df[df["Data"].dt.date == data_dx]
        dati_dx = {}

        for ruota in ruote:
            try:
                numeri = estrazione_dx[[f"{ruota}", f"{ruota}.1", f"{ruota}.2", f"{ruota}.3", f"{ruota}.4"]].values.tolist()[0]
                if len(numeri) == 5:
                    dati_dx[ruota] = numeri
                else:
                    dati_dx[ruota] = [None] * 5
            except:
                dati_dx[ruota] = [None] * 5

        df_dx = pd.DataFrame(dati_dx, index=["1º", "2º", "3º", "4º", "5º"]).transpose()

        def style_dx(val):
            if isinstance(val, int) and val in consecutivi_sx:
                return 'color: red; font-weight: bold; font-size: 18px;'
            return ''

        st.dataframe(df_dx.style.applymap(style_dx), use_container_width=False, height=altezza, width=600)
