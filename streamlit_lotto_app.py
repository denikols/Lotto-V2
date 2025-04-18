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

    # Raccogliamo tutti i dati prima di elaborarli
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

    # Per ogni ruota, cerchiamo i numeri consecutivi nella tabella sx e verifichiamo se esistono nella dx
    numeri_evidenziati_sx = {}
    numeri_evidenziati_dx = {}
    
    for ruota in ruote:
        # Trova numeri consecutivi nella tabella di sinistra
        numeri_sx = dati_sx[ruota]
        consecutivi_sx = trova_numeri_consecutivi(numeri_sx)
        
        # Verifica quali di questi numeri esistono anche nella tabella di destra
        numeri_dx = dati_dx[ruota]
        numeri_dx_set = set([int(n) for n in numeri_dx if n is not None and not pd.isna(n)])
        
        # Conserva solo i numeri consecutivi di sx che sono presenti anche in dx
        numeri_comuni = [n for n in consecutivi_sx if int(n) in numeri_dx_set]
        
        # Salva i numeri da evidenziare per ogni ruota
        numeri_evidenziati_sx[ruota] = set(numeri_comuni)
        numeri_evidenziati_dx[ruota] = set(numeri_comuni)

    # Funzione per colorare le celle in base ai numeri evidenziati
    def color_cells(val, ruota, tabella):
        if val is None or pd.isna(val):
            return ''
        
        numeri_evidenziati = numeri_evidenziati_sx if tabella == 'sx' else numeri_evidenziati_dx
        
        if int(val) in numeri_evidenziati[ruota]:
            return 'color: red; background-color: black; font-weight: bold'
        return ''

    # Crea le DataFrame per le tabelle
    tabella_sx = pd.DataFrame(dati_sx, index=["1º", "2º", "3º", "4º", "5º"])
    tabella_dx = pd.DataFrame(dati_dx, index=["1º", "2º", "3º", "4º", "5º"])
    
    # Crea le funzioni di stile specifiche per ogni ruota e tabella
    def make_style_function(ruota, tabella):
        return lambda x: [color_cells(x.iloc[i], ruota, tabella) for i in range(len(x))]

    # Applica lo stile alle tabelle
    styled_tables_sx = []
    styled_tables_dx = []
    
    for ruota in ruote:
        # Per ogni ruota, estrae i dati e applica lo stile
        ruota_data_sx = tabella_sx[[ruota]].transpose()
        ruota_data_dx = tabella_dx[[ruota]].transpose()
        
        styled_ruota_sx = ruota_data_sx.style.apply(make_style_function(ruota, 'sx'), axis=1)
        styled_ruota_dx = ruota_data_dx.style.apply(make_style_function(ruota, 'dx'), axis=1)
        
        styled_tables_sx.append((ruota, styled_ruota_sx))
        styled_tables_dx.append((ruota, styled_ruota_dx))

    # Determina l'opzione di visualizzazione
    st.markdown("## 🧮 Opzioni di Analisi")
    opzioni = ["Numeri consecutivi che appaiono in entrambe le tabelle"]
    opzione_selezionata = st.selectbox("Seleziona tipo di analisi:", opzioni)
    
    # Mostra le tabelle con gli stili
    st.markdown("## 📊 Risultati dell'analisi")
    st.markdown(f"**{opzione_selezionata}** (evidenziati in rosso su sfondo nero)")
    
    col_sx, col_dx = st.columns(2)
    
    with col_sx:
        st.markdown(f"### Tabella Sinistra (Data: {data_sx})")
        for ruota, styled_table in styled_tables_sx:
            st.markdown(f"**{ruota}**")
            st.dataframe(styled_table, use_container_width=False, height=75)
    
    with col_dx:
        st.markdown(f"### Tabella Destra (Data: {data_dx})")
        for ruota, styled_table in styled_tables_dx:
            st.markdown(f"**{ruota}**")
            st.dataframe(styled_table, use_container_width=False, height=75)
