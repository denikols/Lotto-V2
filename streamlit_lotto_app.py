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

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🔎 Tabella sinistra")
        data_sx = st.selectbox("Scegli una data (SX)", date_uniche, key="data_sx")
        estrazione_sx = df[df["Data"].dt.date == data_sx]
        dati_sx = {}

        for ruota in ruote:
            try:
                numeri = estrazione_sx[[f"{ruota}", f"{ruota}.1", f"{ruota}.2", f"{ruota}.3", f"{ruota}.4"]].values.tolist()[0]
                dati_sx[ruota] = numeri if len(numeri) == 5 else [None]*5
            except:
                dati_sx[ruota] = [None]*5

        tabella_sx = pd.DataFrame(dati_sx, index=["1º", "2º", "3º", "4º", "5º"])
        altezza = (len(ruote) + 1) * 40
        st.dataframe(tabella_sx.transpose(), use_container_width=False, height=altezza, width=600)

    with col2:
        st.markdown("### 🔎 Tabella destra")
        data_dx = st.selectbox("Scegli una data (DX)", date_uniche, key="data_dx")
        estrazione_dx = df[df["Data"].dt.date == data_dx]
        dati_dx = {}

        for ruota in ruote:
            try:
                numeri = estrazione_dx[[f"{ruota}", f"{ruota}.1", f"{ruota}.2", f"{ruota}.3", f"{ruota}.4"]].values.tolist()[0]
                dati_dx[ruota] = numeri if len(numeri) == 5 else [None]*5
            except:
                dati_dx[ruota] = [None]*5

        tabella_dx = pd.DataFrame(dati_dx, index=["1º", "2º", "3º", "4º", "5º"])
        st.dataframe(tabella_dx.transpose(), use_container_width=False, height=altezza, width=600)

    # Sezione di analisi sotto le tabelle
    st.markdown("---")
    st.markdown("## 🔍 Analisi Numeri")
    
    # Espandi/collassa le diverse analisi
    with st.expander("🔢 Numeri Consecutivi In Comune", expanded=True):
        st.markdown("Vengono evidenziati i numeri consecutivi presenti in entrambe le estrazioni.")
        
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
        
        # Crea una DataFrame per i risultati
        risultati = {}
        
        for ruota in ruote:
            numeri_sx = dati_sx[ruota]
            numeri_dx = dati_dx[ruota]
            
            # Trova numeri consecutivi in entrambe le tabelle
            consecutivi_sx = trova_numeri_consecutivi(numeri_sx)
            consecutivi_dx = trova_numeri_consecutivi(numeri_dx)
            
            # Trova i numeri che sono in entrambe le liste
            comuni = set(consecutivi_sx).intersection(set(consecutivi_dx))
            
            if comuni:
                risultati[ruota] = sorted(list(comuni))
            else:
                risultati[ruota] = []
        
        # Visualizza i risultati
        col_results = st.columns(3)
        
        ruote_per_colonna = len(ruote) // 3 + (1 if len(ruote) % 3 > 0 else 0)
        
        for i, ruota in enumerate(ruote):
            col_idx = i // ruote_per_colonna
            with col_results[col_idx]:
                numeri_comuni = risultati[ruota]
                
                if numeri_comuni:
                    st.markdown(f"**{ruota}**: " + 
                               ", ".join([f"<span style='color:red; font-weight:bold; font-size:larger'>{num}</span>" 
                                         for num in numeri_comuni]), 
                               unsafe_allow_html=True)
                else:
                    st.markdown(f"**{ruota}**: Nessun numero consecutivo in comune")
    
    # Altre possibili analisi (puoi aggiungerne di più)
    with st.expander("🔄 Altri tipi di analisi"):
        st.markdown("Qui puoi aggiungere altre analisi tra le due estrazioni.")
        st.markdown("Per esempio: numeri che si ripetono, somme, frequenza, etc.")
