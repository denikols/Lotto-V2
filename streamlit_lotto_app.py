import streamlit as st
import pandas as pd
from collections import Counter
from datetime import timedelta
import base64
import numpy as np

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

/* Stili per le strategie di gioco */
.strategy-card {
    border: 1px solid #ddd;
    border-radius: 8px;
    padding: 15px;
    margin-bottom: 15px;
    background-color: #f9f9f9;
}

.strategy-title {
    color: #2C3E50;
    font-weight: bold;
    margin-bottom: 10px;
}

.strategy-description {
    color: #555;
    font-size: 0.9em;
    margin-bottom: 8px;
}

.strategy-alert {
    color: #E74C3C;
    font-weight: bold;
    font-size: 0.9em;
}

.budget-calculator {
    background-color: #EBF5FB;
    border-radius: 8px;
    padding: 12px;
    margin-top: 10px;
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

    # Tabs per separare le diverse funzionalità
    tab1, tab2 = st.tabs(["📊 Analisi Numeri", "🎮 Strategie di Gioco"])
    
    with tab1:
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

    # --- NUOVE FUNZIONI PER STRATEGIE DI GIOCO ---
    def genera_combinazioni_ambo(numeri, limit=10):
        """Genera combinazioni di ambi dai numeri forniti."""
        combinazioni = []
        for i in range(len(numeri)):
            for j in range(i+1, len(numeri)):
                combinazioni.append((numeri[i], numeri[j]))
                if len(combinazioni) >= limit:
                    return combinazioni
        return combinazioni
    
    def genera_combinazioni_terno(numeri, limit=5):
        """Genera combinazioni di terni dai numeri forniti."""
        combinazioni = []
        for i in range(len(numeri)):
            for j in range(i+1, len(numeri)):
                for k in range(j+1, len(numeri)):
                    combinazioni.append((numeri[i], numeri[j], numeri[k]))
                    if len(combinazioni) >= limit:
                        return combinazioni
        return combinazioni
    
    def valuta_numeri_caldi_freddi(df, ruota, n_estrazioni=30):
        """Identifica i numeri caldi (frequenti di recente) e freddi (alta assenza)."""
        cols = [ruota, f"{ruota}.1", f"{ruota}.2", f"{ruota}.3", f"{ruota}.4"]
        
        # Estrai le ultime n estrazioni
        df_recenti = df.sort_values("Data", ascending=False).head(n_estrazioni)
        
        # Conta le frequenze dei numeri
        numeri_recenti = []
        for _, row in df_recenti.iterrows():
            estratti = [int(row[c]) for c in cols if pd.notnull(row[c])]
            numeri_recenti.extend(estratti)
        
        conteggio = Counter(numeri_recenti)
        
        # Identifica numeri caldi (top 15% per frequenza)
        tutti_conteggi = sorted(conteggio.values(), reverse=True)
        soglia_caldi = tutti_conteggi[int(len(tutti_conteggi) * 0.15)] if tutti_conteggi else 0
        
        numeri_caldi = [num for num, count in conteggio.items() if count >= soglia_caldi]
        
        # Calcola ritardi per numeri freddi
        ritardi = {}
        for num in range(1, 91):
            for i, row in df_recenti.iterrows():
                estratti = [int(row[c]) for c in cols if pd.notnull(row[c])]
                if num in estratti:
                    ritardi[num] = i  # Indice di riga rappresenta il ritardo
                    break
                ritardi[num] = n_estrazioni  # Mai estratto nelle ultime n estrazioni
        
        # Identifica numeri freddi (top 15% per ritardo)
        tutti_ritardi = sorted(ritardi.values(), reverse=True)
        soglia_freddi = tutti_ritardi[int(len(tutti_ritardi) * 0.15)] if tutti_ritardi else 0
        
        numeri_freddi = [num for num, rit in ritardi.items() if rit >= soglia_freddi]
        
        return sorted(numeri_caldi), sorted(numeri_freddi)
    
    def calcola_cicli_uscita(df, ruota, num):
        """Calcola il ciclo medio di uscita di un numero su una ruota."""
        cols = [ruota, f"{ruota}.1", f"{ruota}.2", f"{ruota}.3", f"{ruota}.4"]
        
        # Trova tutte le date di estrazione del numero
        date_estrazioni = []
        for _, row in df.sort_values("Data").iterrows():
            estratti = [int(row[c]) for c in cols if pd.notnull(row[c])]
            if num in estratti:
                date_estrazioni.append(row["Data"])
        
        # Calcola giorni tra estrazioni consecutive
        if len(date_estrazioni) < 2:
            return None
        
        intervalli = [(date_estrazioni[i+1] - date_estrazioni[i]).days 
                     for i in range(len(date_estrazioni)-1)]
        
        return sum(intervalli) / len(intervalli) if intervalli else None
    
    def suggerisci_strategia_ciclica(df, ruota, numeri, n_suggeriti=5):
        """Suggerisce numeri basati sui cicli di uscita."""
        cicli = {}
        prossime_uscite = {}
        
        for num in numeri:
            ciclo_medio = calcola_cicli_uscita(df, ruota, num)
            if ciclo_medio:
                cicli[num] = ciclo_medio
                
                # Trova ultima uscita
                ultima_data = None
                for _, row in df.sort_values("Data", ascending=False).iterrows():
                    estratti = [int(row[c]) for c in [ruota, f"{ruota}.1", f"{ruota}.2", f"{ruota}.3", f"{ruota}.4"] if pd.notnull(row[c])]
                    if num in estratti:
                        ultima_data = row["Data"]
                        break
                
                if ultima_data:
                    giorni_da_ultima_uscita = (df["Data"].max() - ultima_data).days
                    prossimita_ciclo = giorni_da_ultima_uscita / ciclo_medio
                    
                    # Più il valore è vicino a 1, più siamo vicini al prossimo ciclo previsto
                    # Se > 1, il numero è "in ritardo" rispetto al suo ciclo
                    prossime_uscite[num] = prossimita_ciclo
        
        # Ordina per priorità: numeri che sono vicini o appena oltre il loro ciclo previsto
        numeri_ordinati = sorted(prossime_uscite.items(), key=lambda x: abs(1 - x[1]) if x[1] <= 1 else abs(1 - x[1]) * 0.5)
        
        return [(num, cicli[num], prossime_uscite[num]) for num, _ in numeri_ordinati[:n_suggeriti]]
    
    def calcola_budget_ottimale(combinazioni, tipo_gioco="ambo"):
        """Calcola il budget consigliato in base alle combinazioni e al tipo di gioco."""
        n_combinazioni = len(combinazioni)
        
        # Costi base per euro giocato
        costi_base = {
            "estratto": 1,
            "ambo": 1,
            "terno": 1,
            "quaterna": 1,
            "cinquina": 1
        }
        
        # Importo minimo consigliato per combinazione
        importi_min = {
            "estratto": 1,
            "ambo": 1,
            "terno": 0.5,
            "quaterna": 0.5,
            "cinquina": 0.5
        }
        
        costo_min = n_combinazioni * costi_base[tipo_gioco] * importi_min[tipo_gioco]
        costo_ottimale = costo_min * 2  # Importo ottimale (doppio del minimo)
        
        return {
            "minimo": round(costo_min, 2),
            "ottimale": round(costo_ottimale, 2),
            "n_combinazioni": n_combinazioni
        }
    
    def genera_sistema_ridotto(numeri, tipo="ambo", limiti=(5, 10)):
        """Genera un sistema ridotto basato sui numeri forniti."""
        if len(numeri) < 5:
            return []
        
        # Algoritmo simplificato per un sistema ridotto
        numeri = numeri[:10]  # Limitiamo a massimo 10 numeri
        
        if tipo == "ambo":
            min_combs, max_combs = limiti
            tutte_combs = []
            
            # Generiamo tutte le combinazioni possibili
            for i in range(len(numeri)):
                for j in range(i+1, len(numeri)):
                    tutte_combs.append((numeri[i], numeri[j]))
            
            # Selezioniamo un sottoinsieme di combinazioni
            np.random.seed(42)  # Per riproducibilità
            indices = np.random.choice(len(tutte_combs), min(max_combs, len(tutte_combs)), replace=False)
            
            return [tutte_combs[i] for i in indices]
        
        elif tipo == "terno":
            min_combs, max_combs = limiti
            tutte_combs = []
            
            # Generiamo un numero limitato di terni per efficienza
            for i in range(len(numeri)):
                for j in range(i+1, len(numeri)):
                    for k in range(j+1, len(numeri)):
                        tutte_combs.append((numeri[i], numeri[j], numeri[k]))
                        if len(tutte_combs) >= max_combs * 2:
                            break
            
            # Selezioniamo un sottoinsieme di combinazioni
            np.random.seed(42)
            indices = np.random.choice(len(tutte_combs), min(max_combs, len(tutte_combs)), replace=False)
            
            return [tutte_combs[i] for i in indices]
        
        return []
    
    # --- FINE NUOVE FUNZIONI ---

    # Contenitore principale per la visualizzazione dei risultati
    with tab1:
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
                
                # Suggerimenti dei numeri migliori per le ruote con punteggio più alto
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
                
    # TAB STRATEGIE DI GIOCO
    with tab2:
        if 'df' in locals() and len(numeri_finali) > 0:
            st.header("🎯 Strategie di Gioco Integrate")
            
            # Selezione per la ruota su cui applicare le strategie
            ruota_strategia = st.selectbox("Scegli la ruota per le strategie di gioco",
                                          options=top_ruote if 'top_ruote' in locals() else ruote,
                                          index=top_ruote.index(ruota_input) if 'top_ruote' in locals() and ruota_input in top_ruote else 0)
            
            # Ottieni numeri migliori per questa ruota
            migliori_numeri = suggerisci_per_ruota(df, ruota_strategia, num_top=10)
            top_numeri = [num for num, _ in migliori_numeri]
            
            # Unisci con i numeri dell'analisi base che sono nella top 20
            numeri_estesi = top_numeri.copy()
            for num in numeri_finali:
                if num not in numeri_estesi:
                    numeri_estesi.append(num)
            
            numeri_estesi = numeri_estesi[:20]  # Limita a 20 numeri
            
            st.subheader("📋 Seleziona Strategia di Gioco")
            
            strategia_selezionata = st.radio(
                "Scegli la strategia da applicare:",
                ["🔄 Strategia Ciclica", "🔥 Strategia Caldo-Freddo", "📊 Sistema Ridotto", "💰 Ottimizzazione Budget"]
            )
            
            # === STRATEGIA CICLICA ===
            if strategia_selezionata == "🔄 Strategia Ciclica":
                st.markdown("""
                <div class="strategy-card">
                    <div class="strategy-title">🔄 Strategia Ciclica</div>
                    <div class="strategy-description">
                        Questa strategia analizza i cicli di uscita dei numeri, calcolando quanti giorni in media passano tra