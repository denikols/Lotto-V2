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

    # Funzione per trovare coppie di numeri consecutivi in una lista di numeri
    def trova_coppie_consecutive(numeri):
        # Converti a int e rimuovi None/NaN
        numeri_validi = [int(n) for n in numeri if n is not None and not pd.isna(n)]
        numeri_validi.sort()
        
        coppie = []
        for i in range(len(numeri_validi) - 1):
            if numeri_validi[i] + 1 == numeri_validi[i+1]:
                coppie.append((numeri_validi[i], numeri_validi[i+1]))
        
        return coppie

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

    # Dizionari per tenere traccia delle coppie consecutive da evidenziare
    coppie_consecutive_sx = {ruota: [] for ruota in ruote}
    coppie_da_evidenziare_dx = {ruota: [] for ruota in ruote}

    # Per ogni ruota, trova le coppie di numeri consecutivi a sinistra
    for ruota in ruote:
        # Trova le coppie consecutive nella tabella sinistra
        coppie_sx = trova_coppie_consecutive(dati_sx[ruota])
        coppie_consecutive_sx[ruota] = coppie_sx
        
        # Per ogni coppia consecutiva trovata a sinistra
        for coppia in coppie_sx:
            # Controlla se entrambi i numeri sono presenti nella tabella destra
            numeri_dx = [int(n) for n in dati_dx[ruota] if n is not None and not pd.isna(n)]
            if coppia[0] in numeri_dx and coppia[1] in numeri_dx:
                # Se entrambi i numeri sono presenti, aggiungi la coppia ai numeri da evidenziare a destra
                coppie_da_evidenziare_dx[ruota].append(coppia)

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
                if val is not None and not pd.isna(val):
                    val_int = int(val)
                    # Evidenzia se il numero è parte di una coppia consecutiva
                    for coppia in coppie_consecutive_sx[ruota]:
                        if val_int in coppia:
                            styles.loc[ruota, col] = 'color: red; background-color: black; font-weight: bold'
        return styles
    
    def highlight_cells_dx(df):
        styles = pd.DataFrame('', index=df.index, columns=df.columns)
        for ruota in df.index:
            for col in df.columns:
                val = df.loc[ruota, col]
                if val is not None and not pd.isna(val):
                    val_int = int(val)
                    # Evidenzia se il numero è parte di una coppia consecutiva che esiste anche a sinistra
                    for coppia in coppie_da_evidenziare_dx[ruota]:
                        if val_int in coppia:
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
    st.markdown("I numeri in **rosso su sfondo nero** sono numeri che fanno parte di coppie consecutive nella tabella di sinistra. Nella tabella di destra vengono evidenziati solo se entrambi i numeri della coppia sono presenti.")
