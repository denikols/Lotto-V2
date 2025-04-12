
import streamlit as st
import pandas as pd
from collections import Counter
from datetime import timedelta

st.set_page_config(page_title="Sistema Lotto", layout="centered")
st.title("🎯 Sistema Lotto - Analisi Completa per Ruota")

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

    n_giocare = st.slider("Quanti numeri vuoi giocare?", min_value=5, max_value=15, value=10)

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
            successivi.update([num-1 if num > 1 else 90, num+1 if num < 90 else 1])
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

    if st.button("📊 Analizza e scegli la ruota migliore"):
        numeri_base = get_numeri_estrazione(data_estrazione, ruota_input)
        diretti, successivi = get_gruppo_numeri(numeri_base)
        numeri_finali = sorted(set(diretti + successivi))

        st.markdown(f"### ✅ Analisi dei numeri: {', '.join(map(str, numeri_finali))}")

        df_stat = calcola_statistiche_ruota(df, numeri_finali, df["Data"].max())
        

        ))

        st.markdown("### 🔁 Ripetizioni nei 5 turni successivi (con ambi e terni)")
        st.markdown(f"<p style='font-size:16px; margin-top:-8px; color:black;'>Estratti base: <b>{', '.join(map(str, diretti))}</b></p>", unsafe_allow_html=True)

        prossime = df[df["Data"] > pd.Timestamp(data_estrazione)].sort_values("Data").head(5)
        col_estrazioni, col_legenda = st.columns([4, 1])

        with col_estrazioni:
            for _, row in prossime.iterrows():
                estratti = [row[f"{best_ruota}"], row[f"{best_ruota}.1"], row[f"{best_ruota}.2"], row[f"{best_ruota}.3"], row[f"{best_ruota}.4"]]
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
                    if num in suggeriti:
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
