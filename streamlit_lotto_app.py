s st
import pandas as pd
from collections import Counter
from datetime import timedelta
import base64
import itertools
import numpy as np
from typing import List, Set, Tuple
import streamlit as st
import pandas as pd
from collections import Counter
from datetime import timedelta
import base64
from itertools import combinations

st.set_page_config(page_title="Sistema Lotto", layout="centered")

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

# Funzione per generare link di download HTML
def create_download_link(content, filename, link_text):
    b64 = base64.b64encode(content.encode()).decode()
    href = f'<a href="data:text/html;charset=utf-8;base64,{b64}" download="{filename}" class="download-button">{link_text}</a>'
    return href

st.title("🎯 Sistema Lotto - Analisi Completa per Ruota con Numeri Spia")

uploaded_file = st.file_uploader("Carica il file CSV delle estrazioni", type="csv")

if uploaded_file:
    # Leggi il file CSV, assumendo che le prime 3 righe sono intestazioni
    df = pd.read_csv(uploaded_file, skiprows=3)
    df["Data"] = pd.to_datetime(df["Data"], errors="coerce")

    ruote = ["Bari", "Cagliari", "Firenze", "Genova", "Milano",
             "Napoli", "Palermo", "Roma", "Torino", "Venezia", "Nazionale"]

    st.success("File caricato correttamente!")

    col1, col2 = st.columns(2)
    with col1:
        ruota_input = st.selectbox("Scegli la ruota per calcolo base", ruote)
    with col2:
        data_estrazione = st.date_input("Data estrazione", value=df["Data"].max().date())

    st.subheader("⚙️ Impostazioni Analisi Numeri Spia")
    numero_spia_input = st.number_input("Inserisci il numero spia da analizzare (1-90)", min_value=1, max_value=90, value=10)
    finestra_analisi_spia = st.slider("Finestra di analisi per numeri spia (ultime N estrazioni)", min_value=50, max_value=1000, value=300, step=50)

    def get_numeri_estrazione(data, ruota):
        row = df[df["Data"] == pd.Timestamp(data)]
        if row.empty:
            return []
        cols = [ruota, f"{ruota}.1", f"{ruota}.2", f"{ruota}.3", f"{ruota}.4"]
        numeri = row[cols].iloc[0].tolist()
        return [int(n) for n in numeri if pd.notnull(n)]

    def get_gruppo_numeri(numeri):
        gruppo = set()
        successivi = set()
        for num in numeri:
            successivi.update([num - 1 if num > 1 else 90, num + 1 if num < 90 else 1])
        return sorted(numeri), sorted(successivi)

    def calcola_statistiche_ruota(df, numeri, max_data):
        punteggi = []
        for ruota in ruote:
            cols = [ruota, f"{ruota}.1", f"{ruota}.2", f"{ruota}.3", f"{ruota}.4"]
            numeri_ruota = df[cols].apply(pd.to_numeric, errors="coerce")

            freq = numeri_ruota.apply(pd.Series.value_counts).sum(axis=1).reindex(numeri, fill_value=0).sum()

            ritardi = []
            for num in numeri:
                trovato = False
                for i, row in df.sort_values("Data", ascending=False).iterrows():
                    estratti = [row[c] for c in cols if pd.notnull(row[c])]
                    if num in estratti:
                        ritardi.append((max_data - row["Data"]).days)
                        trovato = True
                        break
                if not trovato:
                    ritardi.append((max_data - df["Data"].min()).days)
            rit_medio = sum(ritardi) / len(ritardi)

            recenti = df[df["Data"] > max_data - timedelta(days=60)].sort_values("Data", ascending=False).head(10)
            ripetuti = 0
            for _, row in recenti.iterrows():
                estratti = [row[c] for c in cols if pd.notnull(row[c])]
                ripetuti += len(set(estratti) & set(numeri))

            punteggi.append({
                "Ruota": ruota,
                "Frequenze": freq,
                "Ritardo medio": round(rit_medio, 1),
                "Ripetizioni recenti": ripetuti,
                "Punteggio": freq * 0.4 + rit_medio * 0.2 + ripetuti * 1.5
            })
        return pd.DataFrame(punteggi).sort_values("Punteggio", ascending=False)

    def suggerisci_per_ruota(df, ruota, num_top=5):
        """Suggerisce i migliori numeri da giocare per una ruota specifica."""
        cols = [ruota, f"{ruota}.1", f"{ruota}.2", f"{ruota}.3", f"{ruota}.4"]
        
        # Creiamo una lista di tutti i numeri estratti sulla ruota
        tutti_numeri = []
        for _, row in df.iterrows():
            estratti = [row[c] for c in cols if pd.notnull(row[c])]
            tutti_numeri.extend([int(n) for n in estratti])
        
        # Calcola frequenza
        conteggio = Counter(tutti_numeri)
        
        # Calcola ritardi
        ritardi = {}
        for num in range(1, 91):
            ultimo_estratto = None
            for _, row in df.sort_values("Data", ascending=False).iterrows():
                estratti = [int(row[c]) for c in cols if pd.notnull(row[c])]
                if num in estratti:
                    ultimo_estratto = row["Data"]
                    break
            
            if ultimo_estratto:
                ritardi[num] = (df["Data"].max() - ultimo_estratto).days
            else:
                ritardi[num] = 999  # Se mai estratto, alto ritardo

        # Calcola punteggio combinato (frequenza * 0.4 + ritardo * 0.6)
        punteggi = {}
        for num in range(1, 91):
            freq = conteggio.get(num, 0)
            rit = ritardi.get(num, 999)
            
            # Normalizza la frequenza (più è alta, meglio è)
            freq_norm = freq / max(conteggio.values()) if conteggio else 0
            
            # Normalizza il ritardo (più è alto, meglio è - perché è più probabile che esca)
            rit_norm = rit / max(ritardi.values()) if ritardi else 0
            
            punteggi[num] = freq_norm * 0.4 + rit_norm * 0.6
        
        # Ordina numeri per punteggio e restituisci i top
        numeri_ordinati = sorted(punteggi.items(), key=lambda x: x[1], reverse=True)
        return numeri_ordinati[:num_top]

    def analizza_numeri_spia(df, numero_spia, ruota, finestra):
        df_ruota = df[[ruota, f"{ruota}.1", f"{ruota}.2", f"{ruota}.3", f"{ruota}.4", "Data"]].dropna()
        df_ruota_sorted = df_ruota.sort_values(by="Data", ascending=False).head(finestra).reset_index(drop=True)

        numeri_successivi = Counter()
        for i in range(len(df_ruota_sorted) - 1):
            estrazione_corrente = [int(x) for x in df_ruota_sorted.iloc[i][0:5].tolist()]
            estrazione_successiva = [int(x) for x in df_ruota_sorted.iloc[i + 1][0:5].tolist()]

            if numero_spia in estrazione_corrente:
                numeri_successivi.update(estrazione_successiva)

        totale_uscite_spia = sum(1 for index, row in df_ruota_sorted.iterrows() if numero_spia in [int(x) for x in row[0:5].tolist()])
        if totale_uscite_spia > 0:
            probabilita_successiva = {num: count / totale_uscite_spia for num, count in numeri_successivi.items()}
            probabilita_ordinata = sorted(probabilita_successiva.items(), key=lambda item: item[1], reverse=True)[:5]  # Limita a 5 numeri
            return probabilita_ordinata
        else:
            return []

    # Contenitore principale per la visualizzazione dei risultati
    results_container = st.container()
    
    with results_container:
        st.subheader("🔮 Numeri Suggeriti per i Prossimi Turni (massimo 5)")
        risultati_spia = analizza_numeri_spia(df, numero_spia_input, ruota_input, finestra_analisi_spia)

        if risultati_spia:
            numeri_suggeriti = [f"**{int(num)}** ({probabilita:.2%})" for num, probabilita in risultati_spia]
            st.markdown(f"<p style='font-size:16px; color:green;'>Basati sull'analisi del numero spia <b>{numero_spia_input}</b> sulla ruota di <b>{ruota_input}</b>, i numeri con maggiore probabilità di uscire nei prossimi turni sono: <br> {', '.join(numeri_suggeriti)}</p>", unsafe_allow_html=True)
        else:
            st.info(f"L'analisi del numero spia {numero_spia_input} sulla ruota di {ruota_input} non ha prodotto suggerimenti significativi (il numero spia potrebbe non essere uscito abbastanza frequentemente nella finestra analizzata).")

        if 'df' in locals(): # Verifica se il DataFrame è stato creato
            numeri_base = get_numeri_estrazione(data_estrazione, ruota_input)
            diretti, successivi = get_gruppo_numeri(numeri_base)
            numeri_finali = sorted(set(diretti + successivi))

            st.markdown(f"### ✅ Analisi dei numeri: {', '.join(map(str, numeri_finali))}")

            df_stat = calcola_statistiche_ruota(df, numeri_finali, df["Data"].max())
            st.subheader("📊 Statistiche per Ruota (Numeri Analizzati)")
            st.dataframe(df_stat)
            
            # NUOVA SEZIONE: Suggerimenti dei numeri migliori per le ruote con punteggio più alto
            st.subheader("🎲 Numeri Consigliati per Ciascuna Ruota")
            
            # Prendi le prime 5 ruote con punteggio più alto
            top_ruote = df_stat.head(5)["Ruota"].tolist()
            
            # Versione con tabs per la visualizzazione normale
            tabs = st.tabs([f"Ruota {ruota}" for ruota in top_ruote])
            
            for i, ruota in enumerate(top_ruote):
                with tabs[i]:
                    st.markdown(f"#### 🎯 I migliori numeri da giocare sulla ruota di {ruota}")
                    migliori_numeri = suggerisci_per_ruota(df, ruota, num_top=10)
                    
                    # Crea due colonne
                    col1, col2 = st.columns(2)
                    
                    # Nella prima colonna, mostra i numeri
                    with col1:
                        numeri_html = []
                        for num, score in migliori_numeri:
                            # Colora di verde se è nei numeri originali
                            if num in numeri_finali:
                                numeri_html.append(f"<span style='color:green; font-weight:bold;'>{num}</span> ({score:.2f})")
                            else:
                                numeri_html.append(f"{num} ({score:.2f})")
                        
                        st.markdown(", ".join(numeri_html), unsafe_allow_html=True)
                    
                    # Nella seconda colonna, mostra una leggenda
                    with col2:
                        st.markdown("""
                        **Legenda**:
                        - <span style='color:green; font-weight:bold;'>Verde</span>: Numeri presenti nell'analisi iniziale
                        - Punteggio: Combinazione di frequenza e ritardo
                        """, unsafe_allow_html=True)
                    
                    # Mostra anche l'ultimo turno in cui sono usciti
                    st.markdown("#### Ultima estrazione su questa ruota:")
                    ultima_estrazione = df.sort_values("Data", ascending=False).iloc[0]
                    data_ultima = ultima_estrazione["Data"].date()
                    numeri_ultima = [int(ultima_estrazione[f"{ruota}{'' if i==0 else '.'+str(i)}"]) for i in range(5) if pd.notnull(ultima_estrazione[f"{ruota}{'' if i==0 else '.'+str(i)}"]) ]
                    
                    st.markdown(f"Data: **{data_ultima}** - Numeri estratti: **{', '.join(map(str, numeri_ultima))}**")

            st.markdown("### 🔁 Ripetizioni nei 5 turni successivi (con ambi e terni)")
            st.markdown(f"<p style='font-size:16px; margin-top:-8px; color:black;'>Estratti base: <b>{', '.join(map(str, diretti))}</b></p>", unsafe_allow_html=True)

            prossime = df[df["Data"] > pd.Timestamp(data_estrazione)].sort_values("Data").head(5)
            col_estrazioni, col_legenda = st.columns([4, 1])

            with col_estrazioni:
                for _, row in prossime.iterrows():
                    estratti = [row[f"{ruota_input}"], row[f"{ruota_input}.1"], row[f"{ruota_input}.2"], row[f"{ruota_input}.3"], row[f"{ruota_input}.4"]]
                    estratti = [int(n) for n in estratti if pd.notnull(n)]
                    colorati = []
                    count_estratti = 0
                    for num in estratti:
                        if num in diretti:
                            colorati.append(f"<span style='color:green'><b>{num}</b></span>")
                        elif num in successivi:
                            colorati.append(f"<span style='color:orange'><b>{num}</b></span>")
                        else:
                            colorati.append(f"<span style='color:black'>{num}</span>")
                        if num in numeri_finali:
                            count_estratti += 1
                    simbolo = ""
                    if count_estratti >= 3:
                        simbolo = "<span style='color:red; font-size:22px'><b>T</b></span>"
                    elif count_estratti == 2:
                        simbolo = "<span style='color:red; font-size:22px'><b>A</b></span>"
                    st.markdown(f"🗓️ {row['Data'].date()} → Usciti: " + ", ".join(colorati) + f" {simbolo}", unsafe_allow_html=True)

            with col_legenda:
                st.markdown("""
        <span style='color:green'><b>Verde</b></span>: Estratti base<br>
        <span style='color:orange'><b>Arancione</b></span>: Precedenti/Successivi<br>
        <span style='color:red; font-size:18px'><b>A</b></span>: Ambo<br>
        <span style='color:red; font-size:18px'><b>T</b></span>: Terno
                """, unsafe_allow_html=True)
            # Analisi dei 15 numeri
st.markdown("### 🎯 Analisi Approfondita dei 15 Numeri")

tab1, tab2, tab3, tab4 = st.tabs(["Forza e Pattern", "Combinazioni", "Ciclicità", "Statistiche Avanzate"])

def analizza_forza_pattern(df, ruota, numeri_base, numeri_ant_succ, data_riferimento):
    risultati = {}
    
    # Analisi frequenza e posizioni preferite
    freq_pos = {num: [0, 0, 0, 0, 0] for num in numeri_base + numeri_ant_succ}
    for _, row in df.iterrows():
        for i in range(5):
            num = row[f"{ruota}.{i}" if i > 0 else ruota]
            if pd.notnull(num) and int(num) in freq_pos:
                freq_pos[int(num)][i] += 1
    
    # Calcola la forza di ogni numero
    forza_numeri = {}
    for num, pos in freq_pos.items():
        tot_estrazioni = sum(pos)
        pos_preferita = pos.index(max(pos)) + 1
        forza_numeri[num] = {
            'totale_estrazioni': tot_estrazioni,
            'posizione_preferita': pos_preferita,
            'distribuzione': [f"{(p/tot_estrazioni)*100:.1f}%" if tot_estrazioni > 0 else "0%" for p in pos]
        }
    
    risultati['forza_numeri'] = forza_numeri
    
    # Analisi ultimo mese
    ultimo_mese = df[df['Data'] > pd.Timestamp(data_riferimento) - pd.Timedelta(days=30)]
    freq_ultimo_mese = {num: 0 for num in numeri_base + numeri_ant_succ}
    for _, row in ultimo_mese.iterrows():
        estratti = [row[f"{ruota}.{i}" if i > 0 else ruota] for i in range(5)]
        estratti = [int(n) for n in estratti if pd.notnull(n)]
        for num in estratti:
            if num in freq_ultimo_mese:
                freq_ultimo_mese[num] += 1
    
    risultati['freq_ultimo_mese'] = freq_ultimo_mese
    
    return risultati
    def analizza_combinazioni(df, ruota, numeri_base, numeri_ant_succ, data_riferimento):
    risultati = {}
    
    # Analisi delle coppie più frequenti
    coppie = list(combinations(numeri_base + numeri_ant_succ, 2))
    freq_coppie = {coppia: 0 for coppia in coppie}
    
    # Analisi delle sequenze (numeri consecutivi)
    sequenze = []
    numeri_ordinati = sorted(numeri_base + numeri_ant_succ)
    seq_corrente = [numeri_ordinati[0]]
    
    for i in range(1, len(numeri_ordinati)):
        if numeri_ordinati[i] == numeri_ordinati[i-1] + 1:
            seq_corrente.append(numeri_ordinati[i])
        else:
            if len(seq_corrente) >= 2:
                sequenze.append(seq_corrente.copy())
            seq_corrente = [numeri_ordinati[i]]
    
    if len(seq_corrente) >= 2:
        sequenze.append(seq_corrente)
    
    # Analizza le ultime 50 estrazioni
    ultime_50 = df.sort_values('Data', ascending=False).head(50)
    for _, row in ultime_50.iterrows():
        estratti = [row[f"{ruota}.{i}" if i > 0 else ruota] for i in range(5)]
        estratti = [int(n) for n in estratti if pd.notnull(n)]
        
        # Controlla le coppie
        for i in range(len(estratti)):
            for j in range(i+1, len(estratti)):
                coppia = tuple(sorted([estratti[i], estratti[j]]))
                if coppia in freq_coppie:
                    freq_coppie[coppia] += 1
    
    # Ordina le coppie per frequenza
    coppie_ordinate = sorted(freq_coppie.items(), key=lambda x: x[1], reverse=True)
    risultati['coppie_frequenti'] = [(coppia, freq) for coppia, freq in coppie_ordinate if freq > 0]
    risultati['sequenze'] = sequenze
    
    return risultati
  def analizza_ciclicita(df, ruota, numeri_base, numeri_ant_succ, data_riferimento):
    risultati = {}
    
    # Analisi per giorno della settimana
    freq_giorni = {num: {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0} 
                  for num in numeri_base + numeri_ant_succ}
    
    # Analisi per mese
    freq_mesi = {num: {i: 0 for i in range(1, 13)} 
                for num in numeri_base + numeri_ant_succ}
    
    # Analisi intervalli tra estrazioni
    intervalli = {num: [] for num in numeri_base + numeri_ant_succ}
    ultima_estrazione = {num: None for num in numeri_base + numeri_ant_succ}
    
    for _, row in df.iterrows():
        giorno = row['Data'].dayofweek
        mese = row['Data'].month
        estratti = [int(row[f"{ruota}.{i}" if i > 0 else ruota]) 
                   for i in range(5) if pd.notnull(row[f"{ruota}.{i}" if i > 0 else ruota])]
        
        for num in numeri_base + numeri_ant_succ:
            if num in estratti:
                freq_giorni[num][giorno] += 1
                freq_mesi[num][mese] += 1
                
                if ultima_estrazione[num] is not None:
                    intervallo = (row['Data'] - ultima_estrazione[num]).days
                    intervalli[num].append(intervallo)
                ultima_estrazione[num] = row['Data']
    
    # Calcola le statistiche degli intervalli
    stat_intervalli = {}
    for num, interv in intervalli.items():
        if interv:
            stat_intervalli[num] = {
                'min': min(interv),
                'max': max(interv),
                'media': sum(interv) / len(interv),
                'ultimo': interv[0] if interv else None
            }
        else:
            stat_intervalli[num] = {'min': None, 'max': None, 'media': None, 'ultimo': None}
    
    risultati['freq_giorni'] = freq_giorni
    risultati['freq_mesi'] = freq_mesi
    risultati['intervalli'] = stat_intervalli
    
    return risultati  
   def analizza_statistiche_avanzate(df, ruota, numeri_base, numeri_ant_succ, data_riferimento):
    risultati = {}
    
    # Analisi distribuzione per decine
    decine = {i: [] for i in range(9)}
    for num in numeri_base + numeri_ant_succ:
        decina = (num - 1) // 10
        decine[decina].append(num)
    
    # Conta pari e dispari
    pari = len([n for n in numeri_base + numeri_ant_succ if n % 2 == 0])
    dispari = len(numeri_base + numeri_ant_succ) - pari
    
    # Analisi figure geometriche (triangoli)
    def forma_triangolo(p1, p2, p3):
        # Verifica se tre punti possono formare un triangolo
        return (p1 + p2 > p3) and (p2 + p3 > p1) and (p3 + p1 > p2)
    
    triangoli = []
    for i in range(len(numeri_base + numeri_ant_succ)-2):
        for j in range(i+1, len(numeri_base + numeri_ant_succ)-1):
            for k in range(j+1, len(numeri_base + numeri_ant_succ)):
                nums = sorted([numeri_base + numeri_ant_succ[i], 
                             numeri_base + numeri_ant_succ[j], 
                             numeri_base + numeri_ant_succ[k]])
                if forma_triangolo(nums[0], nums[1], nums[2]):
                    triangoli.append(nums)
    
    # Analisi ultime 10 estrazioni
    ultime_10 = df.sort_values('Data', ascending=False).head(10)
    somme_estratti = []
    distanze_consecutive = []
    
    for _, row in ultime_10.iterrows():
        estratti = sorted([int(row[f"{ruota}.{i}" if i > 0 else ruota]) 
                         for i in range(5) if pd.notnull(row[f"{ruota}.{i}" if i > 0 else ruota])])
        somme_estratti.append(sum(estratti))
        
        for i in range(len(estratti)-1):
            distanze_consecutive.append(estratti[i+1] - estratti[i])
    
    media_somma = sum(somme_estratti) / len(somme_estratti) if somme_estratti else 0
    media_distanza = sum(distanze_consecutive) / len(distanze_consecutive) if distanze_consecutive else 0
    
    risultati['distribuzione_decine'] = decine
    risultati['pari_dispari'] = {'pari': pari, 'dispari': dispari}
    risultati['triangoli'] = triangoli
    risultati 
     # Esegui le analisi
with tab1:
    st.markdown("#### 💪 Forza dei Numeri e Pattern")
    risultati_forza = analizza_forza_pattern(df, ruota_input, diretti, successivi, data_estrazione)
    
    # Visualizza risultati forza
    for num, stats in risultati_forza['forza_numeri'].items():
        col1, col2, col3 = st.columns([1, 2, 2])
        with col1:
            st.metric(f"Numero {num}", f"{stats['totale_estrazioni']} estrazioni")
        with col2:
            st.write(f"Posizione preferita: {stats['posizione_preferita']}ª")
        with col3:
            st.write(f"Distribuzione: {' | '.join(stats['distribuzione'])}")
    
    # Visualizza frequenze ultimo mese
    st.markdown("#### 📅 Frequenze Ultimo Mese")
    freq_mese = pd.DataFrame(list(risultati_forza['freq_ultimo_mese'].items()), 
                           columns=['Numero', 'Frequenza'])
    st.bar_chart(freq_mese.set_index('Numero'))

with tab2:
    st.markdown("#### 🔄 Analisi Combinazioni")
    risultati_comb = analizza_combinazioni(df, ruota_input, diretti, successivi, data_estrazione)
    
    # Visualizza coppie frequenti
    st.markdown("##### Coppie più frequenti:")
    for (n1, n2), freq in risultati_comb['coppie_frequenti'][:10]:
        st.write(f"({n1}, {n2}): {freq} volte")
    
    # Visualizza sequenze
    st.markdown("##### Sequenze di numeri consecutivi:")
    for seq in risultati_comb['sequenze']:
        st.write(f"→ {' → '.join(map(str, seq))}")

with tab3:
    st.markdown("#### 🔄 Analisi Ciclicità")
    risultati_cicli = analizza_ciclicita(df, ruota_input, diretti, successivi, data_estrazione)
    
    # Visualizza frequenze per giorno
    st.markdown("##### Frequenze per giorno della settimana:")
    giorni = ['Lunedì', 'Martedì', 'Mercoledì', 'Giovedì', 'Venerdì', 'Sabato', 'Domenica']
    for num in diretti + successivi:
        freq = risultati_cicli['freq_giorni'][num]
        st.write(f"Numero {num}:")
        for g_idx, giorno in enumerate(giorni):
            st.write(f"- {giorno}: {freq[g_idx]} volte")
        st.write("---")

with tab4:
    st.markdown("#### 📊 Statistiche Avanzate")
    risultati_stat = analizza_statistiche_avanzate(df, ruota_input, diretti, successivi, data_estrazione)
    
    # Visualizza distribuzione decine
    st.markdown("##### Distribuzione per decine:")
    for decina, numeri in risultati_stat['distribuzione_decine'].items():
        if numeri:
            st.write(f"Decina {decina}0-{decina}9: {', '.join(map(str, numeri))}")
    
    # Visualizza pari/dispari
    pari_dispari = risultati_stat['pari_dispari']
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Numeri pari", pari_dispari['pari'])
    with col2:
        st.metric("Numeri dispari", pari_dispari['dispari'])
    
    # Visualizza medie
    st.markdown("##### Medie ultime 10 estrazioni:")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Media somma estratti", f"{risultati_stat['media_somma_estratti']:.1f}")
    with col2:
        st.metric("Media distanza consecutivi", f"{risultati_stat['media_distanza_consecutivi']:.1f}")
            # Crea report stampabile in formato HTML
            report_html = f"""
            <html>
            <head>
                <title>Report Lotto - {pd.Timestamp.now().strftime("%d/%m/%Y")}</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    h1, h2, h3 {{ color: #333; }}
                    table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; }}
                    table, th, td {{ border: 1px solid #ddd; }}
                    th, td {{ padding: 8px; text-align: left; }}
                    .green {{ color: green; font-weight: bold; }}
                    .orange {{ color: orange; font-weight: bold; }}
                    .red {{ color: red; font-weight: bold; }}
                    .header {{ text-align: center; margin-bottom: 20px; }}
                    .footer {{ text-align: center; margin-top: 20px; border-top: 1px solid #ccc; padding-top: 10px; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>Report Analisi Lotto</h1>
                    <p>Data generazione: {pd.Timestamp.now().strftime("%d/%m/%Y %H:%M")}</p>
                    <hr>
                </div>
                
                <h2>🔮 Numeri Suggeriti per i Prossimi Turni</h2>
                <p>Basati sull'analisi del numero spia <b>{numero_spia_input}</b> sulla ruota di <b>{ruota_input}</b></p>
                """
            
            # Aggiungi risultati dell'analisi spia
            if risultati_spia:
                report_html += "<p>I numeri con maggiore probabilità di uscire sono:</p><ul>"
                for num, prob in risultati_spia:
                    report_html += f"<li><b>{num}</b> ({prob:.2%})</li>"
                report_html += "</ul>"
            
            # Aggiungi info sui numeri analizzati
            report_html += f"""
                <h2>✅ Analisi dei numeri: {', '.join(map(str, numeri_finali))}</h2>
                <p>Estratti base: <b>{', '.join(map(str, diretti))}</b></p>
                <p>Numeri successivi/precedenti: <b>{', '.join(map(str, successivi))}</b></p>
                
                <h2>📊 Statistiche per Ruota</h2>
                <table>
                    <tr>
                        <th>Ruota</th>
                        <th>Frequenze</th>
                        <th>Ritardo medio</th>
                        <th>Ripetizioni recenti</th>
                        <th>Punteggio</th>
                    </tr>
            """
            
            # Aggiungi dati della tabella statistiche
            for _, row in df_stat.iterrows():
                report_html += f"""
                    <tr>
                        <td>{row['Ruota']}</td>
                        <td>{row['Frequenze']}</td>
                        <td>{row['Ritardo medio']}</td>
                        <td>{row['Ripetizioni recenti']}</td>
                        <td><b>{row['Punteggio']:.2f}</b></td>
                    </tr>
                """
            
            report_html += "</table>"
            
            # Aggiungi numeri consigliati per le top ruote
            report_html += "<h2>🎲 Numeri Consigliati per le Ruote Principali</h2>"
            
            for ruota in top_ruote:
                report_html += f"<h3>Ruota di {ruota}</h3>"
                migliori_numeri = suggerisci_per_ruota(df, ruota, num_top=10)
                
                report_html += "<p>Numeri consigliati: "
                numeri_formattati = []
                for num, score in migliori_numeri:
                    if num in numeri_finali:
                        numeri_formattati.append(f"<span class='green'>{num}</span> ({score:.2f})")
                    else:
                        numeri_formattati.append(f"{num} ({score:.2f})")
                
                report_html += ", ".join(numeri_formattati) + "</p>"
                
                # Aggiungi ultima estrazione
                ultima_estrazione = df.sort_values("Data", ascending=False).iloc[0]
                data_ultima = ultima_estrazione["Data"].date()
                numeri_ultima = [int(ultima_estrazione[f"{ruota}{'' if i==0 else '.'+str(i)}"]) for i in range(5) if pd.notnull(ultima_estrazione[f"{ruota}{'' if i==0 else '.'+str(i)}"]) ]
                
                report_html += f"<p>Ultima estrazione ({data_ultima}): <b>{', '.join(map(str, numeri_ultima))}</b></p>"
            
            # Aggiungi sezione ripetizioni
            report_html += """
                <h2>🔁 Ripetizioni nei 5 turni successivi</h2>
                <p><span class='green'>Verde</span>: Estratti base, 
                <span class='orange'>Arancione</span>: Numeri successivi/precedenti, 
                <span class='red'>A</span>: Ambo, 
                <span class='red'>T</span>: Terno</p>
                <table>
                    <tr><th>Data</th><th>Numeri estratti</th><th>Note</th></tr>
            """
            
            for _, row in prossime.iterrows():
                estratti = [row[f"{ruota_input}"], row[f"{ruota_input}.1"], row[f"{ruota_input}.2"], row[f"{ruota_input}.3"], row[f"{ruota_input}.4"]]
                estratti = [int(n) for n in estratti if pd.notnull(n)]
                colorati = []
                count_estratti = 0
                
                for num in estratti:
                    if num in diretti:
                        colorati.append(f"<span class='green'>{num}</span>")
                    elif num in successivi:
                        colorati.append(f"<span class='orange'>{num}</span>")
                    else:
                        colorati.append(f"{num}")
                    if num in numeri_finali:
                        count_estratti += 1
                
                simbolo = ""
                if count_estratti >= 3:
                    simbolo = "<span class='red'>T</span>"
                elif count_estratti == 2:
                    simbolo = "<span class='red'>A</span>"
                
                report_html += f"<tr><td>{row['Data'].date()}</td><td>{', '.join(colorati)}</td><td>{simbolo}</td></tr>"
            
            report_html += """
                </table>
                
                <div class="footer">
                    <p>Sistema Lotto - Analisi generata automaticamente</p>
                </div>
            </body>
            </html>
            """
            
            # Mostra pulsanti per stampa e download
            st.markdown("## 🖨️ Stampa e Salvataggio")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(create_download_link(
                    report_html, 
                    f"report_lotto_{pd.Timestamp.now().strftime('%Y%m%d')}.html",
                    "📥 Scarica Report HTML"
                ), unsafe_allow_html=True)
                
            with col2:
                # Pulsante per stampare direttamente dalla pagina
                st.markdown("""
                <a href="#" onclick="window.print()" class="download-button">🖨️ Stampa questa pagina</a>
                """, unsafe_allow_html=True)
            
            st.info("💡 Per stampare il report completo:\n"
                    "1. Clicca su 'Stampa questa pagina' o usa CTRL+P (⌘+P su Mac)\n"
                    "2. Oppure scarica il report HTML e aprilo nel tuo browser")
            # Aggiungi una linea di separazione prima della nuova sezione
            st.markdown("---")
            
            # NUOVA SEZIONE: SISTEMI RIDOTTI
            st.header("🎲 Generatore di Sistemi Ridotti")
            
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
            col1, col2 = st.columns(2)
            
            with col1:
                usa_numeri_analisi = st.checkbox("Usa i numeri dall'analisi precedente", value=True)
                
            with col2:
                if usa_numeri_analisi and 'numeri_finali' in locals():
                    numeri_sistema = numeri_finali
                    st.write(f"Numeri selezionati: {', '.join(map(str, sorted(numeri_sistema)))}")
                else:
                    numeri_input = st.text_input("Inserisci i numeri separati da virgola (es: 1,2,3,4,5)", "")
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