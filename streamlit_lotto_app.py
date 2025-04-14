import streamlit as st
import pandas as pd
import datetime

# Configurazione della pagina
st.set_page_config(page_title="Analisi Estrazioni Lotto", page_icon="🎲")

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
        
        # Conversione della colonna data (assumendo che esista una colonna 'data')
        # Modifica il nome della colonna se necessario nel tuo CSV
        df['data'] = pd.to_datetime(df['data'])
        
        # Selezione della ruota
        st.header("Seleziona la ruota")
        ruota_selezionata = st.selectbox("Scegli la ruota da analizzare", RUOTE)
        
        # Selezione della data
        st.header("Seleziona la data")
        min_date = df['data'].min()
        max_date = df['data'].max()
        data_selezionata = st.date_input(
            "Scegli la data da analizzare",
            min_value=min_date,
            max_value=max_date,
            value=max_date
        )
        
        # Filtraggio dei dati
        dati_filtrati = df[
            (df['ruota'] == ruota_selezionata.lower()) & 
            (df['data'].dt.date == data_selezionata)
        ]
        
        # Visualizzazione dei risultati
        st.header("Risultati dell'estrazione")
        if not dati_filtrati.empty:
            st.write(f"Estrazione del {data_selezionata} - Ruota di {ruota_selezionata}")
            # Assumendo che ci siano colonne per i 5 numeri estratti
            # Modifica i nomi delle colonne in base al tuo CSV
            numeri_estratti = dati_filtrati[['numero1', 'numero2', 'numero3', 'numero4', 'numero5']]
            st.write(numeri_estratti)
            
            # Visualizzazione grafica dei numeri
            st.bar_chart(numeri_estratti.T)
        else:
            st.warning("Nessuna estrazione trovata per la data e la ruota selezionate")
        
        # Statistiche aggiuntive
        st.header("Statistiche")
        if not dati_filtrati.empty:
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Somma dei numeri", dati_filtrati[['numero1', 'numero2', 'numero3', 'numero4', 'numero5']].sum(axis=1).values[0])
            with col2:
                st.metric("Media dei numeri", round(dati_filtrati[['numero1', 'numero2', 'numero3', 'numero4', 'numero5']].mean(axis=1).values[0], 2))
        
    except Exception as e:
        st.error(f"Si è verificato un errore durante la lettura del file: {str(e)}")
        st.write("Assicurati che il file CSV contenga le colonne corrette: data, ruota, numero1, numero2, numero3, numero4, numero5")

# Informazioni sul formato del file CSV atteso
st.sidebar.header("Informazioni sul formato CSV")
st.sidebar.write("""
Il file CSV deve contenere le seguenti colonne:
- data: Data dell'estrazione (formato YYYY-MM-DD)
- ruota: Nome della ruota (in minuscolo)
- numero1: Primo numero estratto
- numero2: Secondo numero estratto
- numero3: Terzo numero estratto
- numero4: Quarto numero estratto
- numero5: Quinto numero estratto
""")