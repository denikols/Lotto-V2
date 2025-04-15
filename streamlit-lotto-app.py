import streamlit as st
import pandas as pd
from collections import Counter

st.set_page_config(page_title="Sistema Lotto", layout="centered")

st.title("🎯 Sistema Lotto - Analisi Numeri Spia")

# Caricamento dati
uploaded_file = st.file_uploader("Carica il file CSV delle estrazioni", type="csv")

if uploaded_file:
    # Blocco di codice per il caricamento del file
    try:
        # Tentativo di lettura del file
        df = pd.read_csv(uploaded_file, skiprows=3)
        # Converto la colonna Data
        df["Data"] = pd.to_datetime(df["Data"], errors="coerce")
        
        st.success("File caricato correttamente!")
        
        # Lista delle ruote disponibili
        ruote = ["Bari", "Cagliari", "Firenze", "Genova", "Milano",
                "Napoli", "Palermo", "Roma", "Torino", "Venezia", "Nazionale"]
        
        # Interfaccia utente per i parametri
        col1, col2 = st.columns(2)
        with col1:
            ruota_input = st.selectbox("Scegli la ruota", ruote)
        with col2:
            numero_spia_input = st.number_input("Numero spia (1-90)", min_value=1, max_value=90, value=10)
        
        finestra_analisi_spia = st.slider("Finestra di analisi (ultime N estrazioni)", 
                                          min_value=50, max_value=1000, value=300, step=50)
        
        # Pulsante per avviare l'analisi
        if st.button("Analizza"):
            # Contenitore per mostrare un messaggio durante l'elaborazione
            with st.spinner("Analisi in corso..."):
                # Step 1: Preparo le colonne per la ruota selezionata
                colonne_ruota = []
                for i in range(5):  # Le 5 colonne per ciascuna ruota
                    if i == 0:
                        col_name = ruota_input
                    else:
                        col_name = f"{ruota_input}.{i}"
                    
                    if col_name in df.columns:
                        colonne_ruota.append(col_name)
                
                # Step 2: Filtro le estrazioni per la finestra temporale
                df_filtrato = df.sort_values("Data", ascending=False).head(finestra_analisi_spia).copy()
                
                # Step 3: Analizzo le occorrenze del numero spia
                numeri_successivi = Counter()
                contatore_occorrenze = 0
                
                for i in range(len(df_filtrato) - 1):
                    # Estraggo i numeri dell'estrazione corrente
                    numeri_estrazione_corrente = []
                    for col in colonne_ruota:
                        try:
                            if col in df_filtrato.columns:
                                val = df_filtrato.iloc[i][col]
                                if pd.notna(val):
                                    num = int(float(val))
                                    numeri_estrazione_corrente.append(num)
                        except Exception:
                            pass
                    
                    # Estraggo i numeri dell'estrazione successiva
                    numeri_estrazione_successiva = []
                    for col in colonne_ruota:
                        try:
                            if col in df_filtrato.columns:
                                val = df_filtrato.iloc[i+1][col]
                                if pd.notna(val):
                                    num = int(float(val))
                                    numeri_estrazione_successiva.append(num)
                        except Exception:
                            pass
                    
                    # Verifico se il numero spia è presente nell'estrazione corrente
                    if numero_spia_input in numeri_estrazione_corrente:
                        contatore_occorrenze += 1
                        # Aggiungo i numeri dell'estrazione successiva al counter
                        numeri_successivi.update(numeri_estrazione_successiva)
            
            # Visualizzo i risultati
            st.subheader("🔮 Numeri Suggeriti per i Prossimi Turni")
            
            if contatore_occorrenze > 0:
                # Calcolo le probabilità
                probabilita = {num: count/contatore_occorrenze for num, count in numeri_successivi.items()}
                # Ordino per probabilità decrescente e prendo i primi 5
                top_numeri = sorted(probabilita.items(), key=lambda x: x[1], reverse=True)[:5]
                
                # Visualizzo le statistiche
                st.info(f"Il numero spia {numero_spia_input} è apparso {contatore_occorrenze} volte nelle ultime {finestra_analisi_spia} estrazioni sulla ruota di {ruota_input}.")
                
                # Creo una tabella per mostrare i risultati
                risultati_df = pd.DataFrame(top_numeri, columns=['Numero', 'Probabilità'])
                risultati_df['Probabilità'] = risultati_df['Probabilità'].apply(lambda x: f"{x:.2%}")
                st.dataframe(risultati_df)
                
                # Visualizzo anche in formato testo per maggiore chiarezza
                numeri_formattati = [f"**{int(num)}** ({prob})" for num, prob in zip(risultati_df['Numero'], risultati_df['Probabilità'])]
                st.markdown(f"I numeri più probabili sono: {', '.join(numeri_formattati)}", unsafe_allow_html=True)
            else:
                st.warning(f"Il numero spia {numero_spia_input} non è apparso nelle ultime {finestra_analisi_spia} estrazioni sulla ruota di {ruota_input}.")
    
    except Exception as e:
        st.error(f"Si è verificato un errore: {str(e)}")
        st.info("Controlla che il formato del file CSV sia corretto. Il file dovrebbe contenere una riga di intestazione e le colonne per le ruote.")

else:
    st.info("Carica un file CSV con i dati delle estrazioni per iniziare l'analisi.")
