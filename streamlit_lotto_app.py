import streamlit as st
import pandas as pd
import datetime

# Configurazione della pagina
st.set_page_config(page_title="Analisi Estrazioni Lotto", page_icon="🎲", layout="wide")

# Titolo dell'applicazione
st.title("📊 Analisi Estrazioni Lotto")

# Lista delle ruote del lotto
RUOTE = [
    "Bari", "Cagliari", "Firenze", "Genova", "Milano",
    "Napoli", "Palermo", "Roma", "Torino", "Venezia", "Nazionale"
]

# Caricamento del file CSV
st.header("Carica il file delle estrazioni")
file_csv = st.file_uploader("Seleziona il file CSV delle estrazioni", type=['csv'])

if file_csv is not None:
    try:
        # Lettura del file CSV
        df = pd.read_csv(file_csv)
        
        # Converti la colonna Data in datetime
        df['Data'] = pd.to_datetime(df['Data'])
        
        # Selezione della ruota
        st.header("Seleziona la ruota")
        ruota_selezionata = st.selectbox("Scegli la ruota da analizzare", RUOTE)
        
        # Selezione della data
        st.header("Seleziona la data")
        min_date = df['Data'].min()
        max_date = df['Data'].max()
        
        data_selezionata = st.date_input(
            "Scegli la data da analizzare",
            min_value=min_date,
            max_value=max_date,
            value=max_date
        )
        
        # Filtraggio dei dati per la data selezionata
        data_filtrata = df[df['Data'].dt.date == data_selezionata]
        
        if not data_filtrata.empty:
            st.header(f"Risultati dell'estrazione del {data_selezionata}")
            
            # Estrai i numeri per la ruota selezionata
            colonne_ruota = [col for col in df.columns if ruota_selezionata in col]
            numeri_estratti = data_filtrata[colonne_ruota].iloc[0]
            
            # Visualizzazione dei risultati
            st.subheader(f"Numeri estratti - Ruota di {ruota_selezionata}")
            
            # Creazione di colonne per visualizzare i numeri
            cols = st.columns(5)
            for i, (col, numero) in enumerate(zip(cols, numeri_estratti)):
                with col:
                    st.metric(f"Numero {i+1}", int(numero))
            
            # Visualizzazione grafica
            st.subheader("Grafico dei numeri estratti")
            chart_data = pd.DataFrame([numeri_estratti.values], 
                                    columns=[f"Numero {i+1}" for i in range(5)])
            st.bar_chart(chart_data.T)
            
            # Statistiche
            st.header("Statistiche")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Somma dei numeri", int(numeri_estratti.sum()))
            with col2:
                st.metric("Media dei numeri", round(numeri_estratti.mean(), 2))
            with col3:
                st.metric("Numero più alto", int(numeri_estratti.max()))
            
            # Mostra tutti i risultati del giorno per tutte le ruote
            st.header("Tutte le estrazioni del giorno")
            
            # Crea un DataFrame più leggibile con tutte le ruote
            risultati_giorno = pd.DataFrame()
            for ruota in RUOTE:
                colonne = [col for col in df.columns if ruota in col]
                numeri = data_filtrata[colonne].iloc[0]
                risultati_giorno[ruota] = [', '.join(map(str, map(int, numeri)))]
            
            st.dataframe(risultati_giorno.T)
            
        else:
            st.warning("Nessuna estrazione trovata per la data selezionata")
        
    except Exception as e:
        st.error(f"Si è verificato un errore durante la lettura del file: {str(e)}")
        st.write("Assicurati che il file CSV sia nel formato corretto")

# Informazioni sul formato nella sidebar
st.sidebar.header("Informazioni")
st.sidebar.write("""
Questa applicazione permette di:
- Visualizzare le estrazioni per data
- Analizzare i numeri per ogni ruota
- Vedere statistiche sui numeri estratti
- Confrontare le estrazioni di tutte le ruote
""")