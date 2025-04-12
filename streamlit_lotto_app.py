
import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

st.title("🔍 Analisi Lotto basata su estrazioni e numeri coerenti")

# Upload file CSV
file = st.file_uploader("Carica il file delle estrazioni", type=["csv"])

if file:
    df = pd.read_csv(file)
    
    # Verifica presenza colonna "Data" o simili
    possible_date_cols = [col for col in df.columns if col.lower() == "data"]
    if not possible_date_cols:
        st.error("❌ Il file non contiene una colonna chiamata 'Data'.")
        st.stop()
    df.rename(columns={possible_date_cols[0]: "Data"}, inplace=True)
    df["Data"] = pd.to_datetime(df["Data"])


    ruote = ["Bari", "Cagliari", "Firenze", "Genova", "Milano",
             "Napoli", "Palermo", "Roma", "Torino", "Venezia", "Nazionale"]

    ruota_input = st.selectbox("Seleziona la ruota", ruote)
    data_estrazione = st.date_input("Data estrazione", value=df["Data"].max().date())

    if pd.Timestamp(data_estrazione) not in df["Data"].values:
        st.error("❌ Nessuna estrazione trovata in questa data.")
    else:
        def get_numeri_estrazione(data, ruota):
            riga = df[(df["Data"] == pd.Timestamp(data))]
            numeri = [riga[f"{ruota}"].values[0], riga[f"{ruota}.1"].values[0],
                      riga[f"{ruota}.2"].values[0], riga[f"{ruota}.3"].values[0],
                      riga[f"{ruota}.4"].values[0]]
            return list(map(int, numeri))

        def get_gruppo_numeri(base):
            successivi = []
            for n in base:
                if n > 1:
                    successivi.append(n - 1)
                if n < 90:
                    successivi.append(n + 1)
            return base, successivi

        numeri_base = get_numeri_estrazione(data_estrazione, ruota_input)
        diretti, successivi = get_gruppo_numeri(numeri_base)
        numeri_finali = sorted(set(diretti + successivi))

        # 🔁 Ripetizioni nei 5 turni successivi
        st.markdown("### 🔁 Ripetizioni nei 5 turni successivi (con ambi e terni)")
        st.markdown(f"<p style='font-size:16px; margin-top:-8px; color:black;'>Estratti base: <b>{', '.join(map(str, diretti))}</b></p>", unsafe_allow_html=True)

        prossime = df[df["Data"] > pd.Timestamp(data_estrazione)].sort_values("Data").head(5)
        col_estrazioni, col_legenda = st.columns([4, 1])

        with col_estrazioni:
            for _, row in prossime.iterrows():
                estratti = [row[f"{ruota_input}"], row[f"{ruota_input}.1"],
                            row[f"{ruota_input}.2"], row[f"{ruota_input}.3"],
                            row[f"{ruota_input}.4"]]
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

        # 📊 Analisi combinata dei 15 numeri sulla ruota selezionata
        st.markdown("### 📊 Analisi combinata dei 15 numeri sulla ruota selezionata")
        colpi = st.slider("Seleziona il numero di estrazioni da analizzare", 50, 300, 100, step=10)
        df_filtrato = df[df["Data"] <= pd.Timestamp(data_estrazione)].sort_values("Data", ascending=False).head(colpi)
        cols = [ruota_input, f"{ruota_input}.1", f"{ruota_input}.2", f"{ruota_input}.3", f"{ruota_input}.4"]
        frequenze, ritardi = {}, {}
        affinità = {n: 0 for n in numeri_finali}

        for n in numeri_finali:
            frequenze[n] = 0
            ritardi[n] = colpi * 2

        for _, row in df_filtrato.iterrows():
            estratti = [int(row[c]) for c in cols if pd.notnull(row[c])]
            presenti = [n for n in numeri_finali if n in estratti]
            for n in presenti:
                frequenze[n] += 1
                if ritardi[n] == colpi * 2:
                    ritardi[n] = (pd.Timestamp(data_estrazione) - row["Data"]).days
            if len(presenti) >= 2:
                for n in presenti:
                    affinità[n] += len(presenti) - 1

        risultati = []
        for n in sorted(numeri_finali):
            f = frequenze[n]
            r = ritardi[n]
            a = affinità[n]
            punteggio = (f * 0.4) + (a * 1.2) - (r / 10)
            colore = "green" if punteggio >= 6 else "orange" if punteggio >= 3 else "red"
            risultati.append({
                "Numero": n,
                "Frequenza": f,
                "Ritardo": r,
                "Affinità": a,
                "Punteggio": round(punteggio, 2),
                "Colore": colore
            })

        df_result = pd.DataFrame(risultati).sort_values("Punteggio", ascending=False)
        def evidenzia(r):
            return f"color: {r['Colore']}; font-weight: bold"

        st.dataframe(df_result.drop(columns=["Colore"]).style.apply(evidenzia, axis=1))
