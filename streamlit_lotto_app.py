import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(layout="wide")
st.title("📅 Visualizzatore Estrazioni Lotto - Confronto Due Date")

ruote = ["Bari", "Cagliari", "Firenze", "Genova", "Milano",
         "Napoli", "Palermo", "Roma", "Torino", "Venezia", "Nazionale"]

uploaded_file = st.file_uploader("Carica il file CSV delle estrazioni", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file, skiprows=3)
    df["Data"] = pd.to_datetime(df["Data"], errors="coerce")
    df = df.dropna(subset=["Data"])
    df = df.sort_values("Data", ascending=False)
    date_uniche = df["Data"].dt.date.unique()

    # Funzione per trovare numeri consecutivi in una lista di numeri
    def trova_numeri_consecutivi(numeri):
        # Converti a int e rimuovi None/NaN
        numeri_validi = [int(n) for n in numeri if n is not None and not pd.isna(n)]
        numeri_validi.sort()
        
        consecutivi = []
        for i in range(len(numeri_validi) - 1):
            if numeri_validi[i] + 1 == numeri_validi[i+1]:
                consecutivi.append(numeri_validi[i])
                consecutivi.append(numeri_validi[i+1])
        
        # Rimuovi duplicati mantenendo l'ordine
        return list(dict.fromkeys(consecutivi))

    # Crea due colonne per le tabelle
    col1, col2 = st.columns(2)

    # Tabella sinistra
    with col1:
        st.markdown("### 🔎 Tabella sinistra")
        data_sx = st.selectbox("Scegli una data (SX)", date_uniche, key="data_sx")
        estrazione_sx = df[df["Data"].dt.date == data_sx]
        dati_sx = {}

        # Estrai i numeri per ogni ruota nella tabella sinistra
        for ruota in ruote:
            try:
                numeri = estrazione_sx[[f"{ruota}", f"{ruota}.1", f"{ruota}.2", f"{ruota}.3", f"{ruota}.4"]].values.tolist()[0]
                dati_sx[ruota] = numeri if len(numeri) == 5 else [None]*5
            except:
                dati_sx[ruota] = [None]*5

    # Tabella destra
    with col2:
        st.markdown("### 🔎 Tabella destra")
        data_dx = st.selectbox("Scegli una data (DX)", date_uniche, key="data_dx")
        estrazione_dx = df[df["Data"].dt.date == data_dx]
        dati_dx = {}

        # Estrai i numeri per ogni ruota nella tabella destra
        for ruota in ruote:
            try:
                numeri = estrazione_dx[[f"{ruota}", f"{ruota}.1", f"{ruota}.2", f"{ruota}.3", f"{ruota}.4"]].values.tolist()[0]
                dati_dx[ruota] = numeri if len(numeri) == 5 else [None]*5
            except:
                dati_dx[ruota] = [None]*5

    # Dizionari per tenere traccia dei numeri da evidenziare
    numeri_da_evidenziare_sx = {ruota: set() for ruota in ruote}
    numeri_da_evidenziare_dx = {ruota: set() for ruota in ruote}

    # Per ogni ruota, trova i numeri consecutivi a sinistra
    for ruota in ruote:
        # Trova i numeri consecutivi nella tabella sinistra
        consecutivi_sx = trova_numeri_consecutivi(dati_sx[ruota])
        
        # Aggiungi questi numeri al set dei numeri da evidenziare nella tabella sinistra
        numeri_da_evidenziare_sx[ruota].update(consecutivi_sx)
        
        # Controlla se questi numeri sono presenti anche nella tabella destra
        numeri_dx = dati_dx[ruota]
        for num in consecutivi_sx:
            if num in numeri_dx:
                # Se il numero è presente anche nella tabella destra, evidenzialo
                numeri_da_evidenziare_dx[ruota].add(num)

    # Preparazione dei dati per la visualizzazione
    tabella_sx = pd.DataFrame(dati_sx, index=["1º", "2º", "3º", "4º", "5º"])
    tabella_dx = pd.DataFrame(dati_dx, index=["1º", "2º", "3º", "4º", "5º"])
    
    # Prepara tabelle trasposte
    tabella_sx_t = tabella_sx.transpose()
    tabella_dx_t = tabella_dx.transpose()
    
    # Definizione delle funzioni di stile
    def highlight_cells_sx(df):
        styles = pd.DataFrame('', index=df.index, columns=df.columns)
        for ruota in df.index:
            for col in df.columns:
                val = df.loc[ruota, col]
                if val is not None and not pd.isna(val) and int(val) in numeri_da_evidenziare_sx[ruota]:
                    styles.loc[ruota, col] = 'color: red; background-color: black; font-weight: bold'
        return styles
    
    def highlight_cells_dx(df):
        styles = pd.DataFrame('', index=df.index, columns=df.columns)
        for ruota in df.index:
            for col in df.columns:
                val = df.loc[ruota, col]
                if val is not None and not pd.isna(val) and int(val) in numeri_da_evidenziare_dx[ruota]:
                    styles.loc[ruota, col] = 'color: red; background-color: black; font-weight: bold'
        return styles

    # Mostra le tabelle con l'evidenziazione
    with col1:
        altezza = (len(ruote) + 1) * 40
        st.dataframe(
            tabella_sx_t.style.apply(highlight_cells_sx, axis=None), 
            use_container_width=False, 
            height=altezza, 
            width=600
        )

    with col2:
        st.dataframe(
            tabella_dx_t.style.apply(highlight_cells_dx, axis=None), 
            use_container_width=False, 
            height=altezza, 
            width=600
        )

    # Aggiungi una sezione di spiegazione
    st.markdown("---")
    st.markdown("### 📌 Legenda")
    st.markdown("I numeri in **rosso su sfondo nero** sono numeri consecutivi trovati nella tabella di sinistra che appaiono anche nella tabella di destra.")
