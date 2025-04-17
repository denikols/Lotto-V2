import streamlit as st
import pandas as pd
import itertools
import numpy as np
from typing import List, Set, Tuple

st.set_page_config(page_title="Sistema Lotto - Generatore di Sistemi Ridotti", layout="centered")

# CSS semplificato per la stampa
st.markdown("""
<style>
@media print {
    .stApp header, .stApp footer, .stSidebar, button, .stToolbar, .stAnnotated, [data-testid="stFileUploadDropzone"] {
        display: none !important;
    }
    
    /* Stile per la stampa */
    body {
        font-size: 12px !important;
    }
    
    h1, h2, h3 {
        margin-top: 10px !important;
        margin-bottom: 5px !important;
    }
    
    /* Assicura che il contenuto sia visibile */
    .element-container, .stAlert, .stDataFrame, .stMarkdown {
        max-width: 100% !important;
        width: 100% !important;
        padding: 0 !important;
        display: block !important;
    }
}

/* Stile per il pulsante personalizzato */
.download-button {
    padding: 0.25rem 0.75rem;
    background-color: #4CAF50;
    color: white !important;
    text-decoration: none;
    border-radius: 4px;
    cursor: pointer;
    display: inline-block;
    margin: 10px 0;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

st.title("🎲 Generatore di Sistemi Ridotti Lotto")

# Funzioni per i sistemi ridotti
def genera_sistema_classico(numeri: List[int], dimensione: int, garanzia: float = 1.0) -> List[Tuple[int, ...]]:
    """
    Genera un sistema ridotto classico.
    """
    tutte_combinazioni = list(itertools.combinations(numeri, dimensione))
    num_combinazioni = int(len(tutte_combinazioni) * garanzia)
    
    sistema_ridotto = []
    numeri_coperti = set()
    
    while len(sistema_ridotto) < num_combinazioni and len(tutte_combinazioni) > 0:
        miglior_combinazione = max(tutte_combinazioni, 
                               key=lambda x: len(set(x) - numeri_coperti))
        
        sistema_ridotto.append(miglior_combinazione)
        numeri_coperti.update(miglior_combinazione)
        tutte_combinazioni.remove(miglior_combinazione)
    
    return sistema_ridotto

def genera_sistema_ortogonale(numeri: List[int], dimensione: int, max_combinazioni: int) -> List[Tuple[int, ...]]:
    """
    Genera un sistema ridotto ortogonale.
    """
    matrice_copertura = np.zeros((len(numeri), len(numeri)))
    tutte_combinazioni = list(itertools.combinations(numeri, dimensione))
    sistema_ridotto = []
    
    while len(sistema_ridotto) < max_combinazioni and tutte_combinazioni:
        punteggi = []
        for comb in tutte_combinazioni:
            idx = [numeri.index(n) for n in comb]
            punteggio = 0
            for i in idx:
                for j in idx:
                    if i != j:
                        punteggio += matrice_copertura[i, j]
            punteggi.append((comb, punteggio))
        
        miglior_combinazione = min(punteggi, key=lambda x: x[1])[0]
        
        idx = [numeri.index(n) for n in miglior_combinazione]
        for i in idx:
            for j in idx:
                if i != j:
                    matrice_copertura[i, j] += 1
        
        sistema_ridotto.append(miglior_combinazione)
        tutte_combinazioni.remove(miglior_combinazione)
    
    return sistema_ridotto

def analizza_sistema(sistema: List[Tuple[int, ...]], numeri_totali: List[int]) -> dict:
    """
    Analizza un sistema ridotto e fornisce statistiche.
    """
    num_combinazioni = len(sistema)
    numeri_coperti = set(n for comb in sistema for n in comb)
    copertura = len(numeri_coperti) / len(numeri_totali)
    
    frequenze = {}
    for num in numeri_totali:
        freq = sum(1 for comb in sistema if num in comb)
        frequenze[num] = freq
    
    return {
        "num_combinazioni": num_combinazioni,
        "copertura": copertura,
        "frequenze": frequenze,
        "costo_sistema": num_combinazioni * 1
    }

# Selezione dei numeri per il sistema
st.subheader("Seleziona i numeri per il sistema")
numeri_input = st.text_input("Inserisci i numeri separati da virgola (es: 1,2,3,4,5,6,7,8,9,10)", "")
try:
    numeri_sistema = [int(n.strip()) for n in numeri_input.split(",") if n.strip()]
    numeri_sistema = [n for n in numeri_sistema if 1 <= n <= 90]
except:
    numeri_sistema = []

if numeri_sistema:
    # Parametri del sistema
    st.subheader("Configura il sistema")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        tipo_sistema = st.selectbox(
            "Tipo di sistema",
            ["Classico", "Ortogonale"]
        )
    
    with col2:
        dimensione = st.selectbox(
            "Tipo di giocata",
            [("Ambo", 2), ("Terno", 3), ("Quaterna", 4)],
            format_func=lambda x: x[0]
        )[1]
    
    with col3:
        if tipo_sistema == "Classico":
            garanzia = st.slider("Livello di garanzia", 0.1, 1.0, 0.8, 0.1)
            max_combinazioni = None
        else:
            max_combinazioni = st.number_input("Numero massimo combinazioni", 5, 100, 20)
            garanzia = None
    
    # Generazione del sistema
    if st.button("Genera Sistema"):
        with st.spinner("Generazione del sistema in corso..."):
            if tipo_sistema == "Classico":
                sistema = genera_sistema_classico(numeri_sistema, dimensione, garanzia)
            else:
                sistema = genera_sistema_ortogonale(numeri_sistema, dimensione, max_combinazioni)
            
            # Analisi del sistema generato
            analisi = analizza_sistema(sistema, numeri_sistema)
            
            # Visualizzazione risultati
            st.subheader("Sistema Generato")
            
            # Statistiche principali
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Combinazioni", analisi["num_combinazioni"])
            with col2:
                st.metric("Copertura", f"{analisi['copertura']:.1%}")
            with col3:
                st.metric("Costo Sistema", f"€{analisi['costo_sistema']:.2f}")
            with col4:
                st.metric("Numeri Utilizzati", len(numeri_sistema))
            
            # Visualizzazione combinazioni
            st.subheader("Combinazioni Generate")
            combinazioni_df = pd.DataFrame(
                [" - ".join(map(str, comb)) for comb in sistema],
                columns=["Combinazione"]
            )
            st.dataframe(combinazioni_df)
            
            # Distribuzione dei numeri
            st.subheader("Distribuzione dei Numeri")
            freq_df = pd.DataFrame(
                list(analisi["frequenze"].items()),
                columns=["Numero", "Frequenza"]
            )
            st.bar_chart(freq_df.set_index("Numero"))
            
            # Export del sistema
            csv = combinazioni_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                "📥 Scarica Sistema (CSV)",
                csv,
                f"sistema_ridotto_{tipo_sistema.lower()}_{len(sistema)}_combinazioni.csv",
                "text/csv",
                key='download-csv'
            )
else:
    st.warning("Inserisci dei numeri validi per generare il sistema")
