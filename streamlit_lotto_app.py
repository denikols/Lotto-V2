import streamlit as st
import pandas as pd
from collections import Counter
from datetime import timedelta
import altair as alt  # Per i grafici

st.set_page_config(page_title="Sistema Lotto", layout="centered")
st.title("🎯 Sistema Lotto - Analisi Completa per Ruota con Numeri Spia")

uploaded_file = st.file_uploader("Carica il file CSV delle estrazioni", type="csv")

if uploaded_file:
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

    def suggerisci_per_ruota(df, numeri, ruota):
        cols = [ruota, f"{ruota}.1", f"{ruota}.2", f"{ruota}.3", f"{ruota}.4"]
        conteggi = Counter()
        ritardi = {}

        for num in numeri:
            count = 0
            ultimo = None
            for _, row in df.sort_values("Data", ascending=False).iterrows():
                estratti = [row[c] for c in cols if pd.notnull(row[c])]
                if num in estratti:
                    if not ultimo:
                        ultimo = row["Data"]
                    count += 1
            conteggi[num] = count
            ritardi[num] = (df["Data"].max() - ultimo).days if ultimo else (df["Data"].max() - df["Data"].min()).days

        ordinati = sorted(numeri, key=lambda x: (conteggi[x], -ritardi[x]), reverse=True)
        return ordinati

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
            probabilita_ordinata = sorted(probabilita_successiva.items(), key=lambda item: item[1], reverse=True)
            return probabilita_ordinata
        else:
            return []

    numeri_base = get_numeri_estrazione(data_estrazione, ruota_input)
    diretti, successivi = get_gruppo_numeri(numeri_base)
    numeri_finali = sorted(set(diretti + successivi))

    st.markdown(f"### ✅ Analisi dei numeri: {', '.join(map(str, numeri_finali))}")

    df_stat = calcola_statistiche_ruota(df, numeri_finali, df["Data"].max())
    st.subheader("📊 Statistiche per Ruota (Numeri Analizzati)")
    st.dataframe(df_stat)

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

    st.subheader(f"🕵️ Analisi Numeri Spia per il Numero {numero_spia_input} sulla Ruota di {ruota_input}")
    risultati_spia = analizza_numeri_spia(df, numero_spia_input, ruota_input, finestra_analisi_spia)

    if risultati_spia:
        st.markdown(f"Probabilità dei numeri di uscire nel turno successivo all'uscita del numero {numero_spia_input} (basata sulle ultime {finestra_analisi_spia} estrazioni):")
        for numero, probabilita in risultati_spia:
            st.markdown(f"- Numero **{numero}**: {probabilita:.2%}")
    else:
        st.info(f"Il numero spia {numero_spia_input} non è stato estratto abbastanza frequentemente nella finestra di analisi per fornire risultati significativi sulla ruota di {ruota_input}.")
