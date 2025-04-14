import streamlit as st
import pandas as pd
from collections import Counter
from datetime import timedelta
import base64
from typing import List, Set, Tuple

st.set_page_config(page_title="Sistema Lotto", layout="centered")

# CSS per la stampa e lo stile
st.markdown("""
<style>
@media print {
    .stApp header, .stApp footer, .stSidebar, button, .stToolbar, .stAnnotated, [data-testid="stFileUploadDropzone"] {
        display: none !important;
    }
    
    body {
        font-size: 12px !important;
    }
    
    h1, h2, h3 {
        margin-top: 10px !important;
        margin-bottom: 5px !important;
    }
    
    .element-container, .stAlert, .stDataFrame, .stMarkdown {
        max-width: 100% !important;
        width: 100% !important;
        padding: 0 !important;
        display: block !important;
    }
}

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

    def analizza_pattern_5_estrazioni(df: pd.DataFrame, data_riferimento: pd.Timestamp, 
                                    ruota: str, numeri_base: List[int], 
                                    numeri_adiacenti: List[int]) -> dict:
        # Prendiamo le ultime 5 estrazioni prima della data di riferimento
        df_analisi = df[df['Data'] <= data_riferimento].sort_values('Data', ascending=False).head(5)
        
        risultati = {
            'ripetizioni': Counter(),
            'ambi_formati': [],
            'settori_attivi': set(),
            'distanze': [],
            'punteggi': {}
        }
        
        # Analizziamo ogni estrazione
        for _, row in df_analisi.iterrows():
            numeri_estratti = [
                int(row[f"{ruota}{'.'+str(i) if i > 0 else ''}"]) 
                for i in range(5) 
                if pd.notnull(row[f"{ruota}{'.'+str(i) if i > 0 else ''}"])
            ]
            
            # 1. Analisi ripetizioni
            for num in numeri_estratti:
                if num in numeri_base or num in numeri_adiacenti:
                    risultati['ripetizioni'][num] += 1
            
            # 2. Analisi ambi
            for i, n1 in enumerate(numeri_estratti):
                for n2 in numeri_estratti[i+1:]:
                    if (n1 in numeri_base and n2 in numeri_base) or \
                       (n1 in numeri_adiacenti and n2 in numeri_adiacenti):
                        risultati['ambi_formati'].append((min(n1, n2), max(n1, n2)))
            
            # 3. Analisi settori
            for num in numeri_estratti:
                settore = (num - 1) // 30 + 1
                risultati['settori_attivi'].add(settore)
            
            # 4. Analisi distanze
            numeri_ordinati = sorted(numeri_estratti)
            for i in range(len(numeri_ordinati)-1):
                dist = numeri_ordinati[i+1] - numeri_ordinati[i]
                risultati['distanze'].append(dist)
        
        # 5. Calcolo punteggi
        tutti_numeri = set(numeri_base + numeri_adiacenti)
        for num in tutti_numeri:
            punteggio = 0
            # Bonus per ripetizioni
            punteggio += risultati['ripetizioni'][num] * 2
            
            # Bonus per ambi formati
            ambi_num = sum(1 for ambo in risultati['ambi_formati'] if num in ambo)
            punteggio += ambi_num * 1.5
            
            # Bonus per settore attivo
            settore_num = (num - 1) // 30 + 1
            if settore_num in risultati['settori_attivi']:
                punteggio += 1
            
            # Malus per distanze non conformi
            dist_media = sum(risultati['distanze']) / len(risultati['distanze']) if risultati['distanze'] else 0
            if abs(num - dist_media) > 20:
                punteggio -= 1
                
            risultati['punteggi'][num] = round(punteggio, 2)
        
        return risultati

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

    # Otteniamo i numeri base e adiacenti
    numeri_base = get_numeri_estrazione(data_estrazione, ruota_input)
    _, numeri_adiacenti = get_gruppo_numeri(numeri_base)
    
    # Analisi base
    st.markdown(f"### ✅ Analisi dei numeri: {', '.join(map(str, sorted(set(numeri_base + numeri_adiacenti))))}")
    df_stat = calcola_statistiche_ruota(df, sorted(set(numeri_base + numeri_adiacenti)), df["Data"].max())
    st.dataframe(df_stat)

    # Analisi Pattern
    st.subheader("📊 Analisi Pattern nelle Ultime 5 Estrazioni")
    
    # Eseguiamo l'analisi
    risultati_pattern = analizza_pattern_5_estrazioni(
        df, 
        pd.Timestamp(data_estrazione), 
        ruota_input,
        numeri_base,
        numeri_adiacenti
    )
    
    # Visualizziamo i risultati
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🔄 Ripetizioni dei Numeri")
        df_ripetizioni = pd.DataFrame(
            [(num, count) for num, count in risultati_pattern['ripetizioni'].items()],
            columns=['Numero', 'Ripetizioni']
        ).sort_values('Ripetizioni', ascending=False)
        st.dataframe(df_ripetizioni)
        
        st.markdown("#### 🎯 Ambi Formati")
        if risultati_pattern['ambi_formati']:
            ambi_str = [f"{a}-{b}" for a, b in risultati_pattern['ambi_formati']]
            st.write(", ".join(ambi_str))
        else:
            st.write("Nessun ambo formato")
    
    with col2:
        st.markdown("#### 🔢 Settori Attivi")
        settori_str = [f"Settore {s}" for s in sorted(risultati_pattern['settori_attivi'])]
        st.write(", ".join(settori_str))
        
        st.markdown("#### 📏 Statistiche Distanze")
        if risultati_pattern['distanze']:
            st.write(f"Media: {sum(risultati_pattern['distanze']) / len(risultati_pattern['distanze']):.1f}")
            st.write(f"Min: {min(risultati_pattern['distanze'])}")
            st.write(f"Max: {max(risultati_pattern['distanze'])}")
    
    # Visualizziamo i punteggi finali
    st.subheader("🏆 Punteggi Finali")
    df_punteggi = pd.DataFrame(
        [(num, score) for num, score in risultati_pattern['punteggi'].items()],
        columns=['Numero', 'Punteggio']
    ).sort_values('Punteggio', ascending=False)
    
    # Evidenziamo i numeri migliori
    top_numeri = df_punteggi.head(10)
    st.markdown("#### 🌟 Top 10 Numeri Consigliati")
    st.dataframe(top_numeri)
    
    # Aggiungiamo un pulsante per scaricare l'analisi
    if st.button("📥 Scarica Analisi Completa"):
        report_html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid black; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <h1>Analisi Pattern - {ruota_input} - {data_estrazione}</h1>
            <h2>Top 10 Numeri Consigliati</h2>
            {top_numeri.to_html()}
            <h2>Dettagli Analisi</h2>
            <p><b>Numeri Base:</b> {', '.join(map(str, numeri_base))}</p>
            <p><b>Numeri Adiacenti:</b> {', '.join(map(str, numeri_adiacenti))}</p>
            <p><b>Settori Attivi:</b> {', '.join(settori_str)}</p>
            <p><b>Ambi Formati:</b> {', '.join([f"{a}-{b}" for a, b in risultati_pattern['ambi_formati']])}</p>
        </body>
        </html>
        """
        st.markdown(
            create_download_link(
                report_html, 
                f"analisi_pattern_{ruota_input}_{data_estrazione}.html",
                "📄 Scarica Report HTML"
            ),
            unsafe_allow_html=True
        )