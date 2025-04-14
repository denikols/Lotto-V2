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
    # Mostra informazioni sul file caricato
    st.write("File caricato:", file_csv.name)
    st.write("Tipo di file:", file_csv.type)
    st.write("Dimensione:", file_csv.size, "bytes")
    
    try:
        # Lettura del file CSV con visualizzazione dei dati grezzi
        st.write("Tentativo di lettura del file...")
        
        # Prova a leggere le prime righe del file come testo
        file_contents = file_csv.getvalue().decode('utf-8')
        st.write("Prime righe del file:")
        st.text(file_contents[:500])  # Mostra i primi 500 caratteri
        
        # Lettura del file CSV
        df = pd.read_csv(file_csv)
        
        # Mostra le informazioni sul DataFrame
        st.write("Struttura del DataFrame:")
        st.write("Numero di righe:", len(df))
        st.write("Colonne presenti:", list(df.columns))
        st.write("Anteprima dei dati:")
        st.write(df.head())
        
        # Verifica la presenza delle colonne necessarie
        colonne_necessarie = ['data', 'ruota', 'numero1', 'numero2', 'numero3', 'numero4', 'numero5']
        colonne_mancanti = [col for col in colonne_necessarie if col not in df.columns]
        
        if colonne_mancanti:
            st.error(f"Attenzione! Mancano le seguenti colonne: {', '.join(colonne_mancanti)}")
            st.stop()
        
        # Conversione della colonna data
        st.write("Conversione della colonna data...")
        df['data'] = pd.to_datetime(df['data'])
        
        # Selezione della ruota
        st.header("Seleziona la ruota")
        ruota_selezionata = st.selectbox("Scegli la ruota da analizzare", RUOTE)
        
        # Selezione della data
        st.header("Seleziona la data")
        min_date = df['data'].min()
        max_date = df['data'].max()
        st.write(f"Range date disponibili: dal {min_date.date()} al {max_date.date()}")
        
        data_selezionata = st.date_input(
            "Scegli la data da analizzare",
            min_value=min_date,
            max_value=max_date,
            value=max_date
        )
        
        # Filtraggio dei dati
        dati_filtrati = df[
            (df['ruota'].str.lower() == ruota_selezionata.lower()) & 
            (df['data'].dt.date == data_selezionata)
        ]
        
        # Visualizzazione dei risultati
        st.header("Risultati dell'estrazione")
        if not dati_filtrati.empty:
            st.write(f"Estrazione del {data_selezionata} - Ruota di {ruota_selezionata}")
            numeri_estratti = dati_filtrati[['numero1', 'numero2', 'numero3', 'numero4', 'numero5']]
            st.write(numeri_estratti)
            
            # Visualizzazione grafica dei numeri
            st.bar_chart(numeri_estratti.T)
            
            # Statistiche
            st.header("Statistiche")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Somma dei numeri", dati_filtrati[['numero1', 'numero2', 'numero3', 'numero4', 'numero5']].sum(axis=1).values[0])
            with col2:
                st.metric("Media dei numeri", round(dati_filtrati[['numero1', 'numero2', 'numero3', 'numero4', 'numero5']].mean(axis=1).values[0], 2))
        else:
            st.warning("Nessuna estrazione trovata per la data e la ruota selezionate")
        
    except Exception as e:
        st.error(f"Si è verificato un errore durante la lettura del file: {str(e)}")
        st.write("Dettagli dell'errore per il debug:", str(e))

# Esempio del formato CSV atteso
st.sidebar.header("Formato CSV richiesto")
st.sidebar.write("""
Il file CSV deve essere strutturato così: