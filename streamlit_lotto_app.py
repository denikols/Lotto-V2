
import streamlit as st
import pandas as pd
from collections import Counter
from datetime import timedelta

st.set_page_config(page_title="Sistema Lotto", layout="centered")
st.title("🎯 Sistema Lotto - Numeri Consigliati e Ripetizioni")

uploaded_file = st.file_uploader("Carica il file CSV delle estrazioni", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file, skiprows=3)
    df["Data"] = pd.to_datetime(df["Data"], errors="coerce")

    ruote = ["Bari", "Cagliari", "Firenze", "Genova", "Milano",
             "Napoli", "Palermo", "Roma", "Torino", "Venezia", "Nazionale"]

    st.success("File caricato correttamente!")

    col1, col2 = st.columns(2)
    with col1:
        ruota = st.selectbox("Scegli la ruota", ruote)
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

    def analizza_successivi(data, ruota):
        prossime = df[df["Data"] > pd.Timestamp(data)].head(5)
        righe = []
        for i, (_, row) in enumerate(prossime.iterrows(), start=1):
            estratti = [row[f"{ruota}"], row[f"{ruota}.1"], row[f"{ruota}.2"], row[f"{ruota}.3"], row[f"{ruota}.4"]]
            estratti = [int(n) for n in estratti if pd.notnull(n)]
            righe.append({"Estrazione n.": i, "Data": row["Data"].date(), "Numeri usciti": estratti})
        return righe

    if st.button("🎲 Calcola numeri da giocare"):
        numeri_base = get_numeri_estrazione(data_estrazione, ruota)
        if not numeri_base:
            st.error("⚠️ Nessun numero trovato per quella data.")
        else:
            diretti, successivi = get_gruppo_numeri(numeri_base)
            gruppo_totale = set(diretti) | set(successivi)

            righe = analizza_successivi(data_estrazione, ruota)
            tutti_successivi = [num for riga in righe for num in riga["Numeri usciti"]]

            rendimento = Counter()
            for num in gruppo_totale:
                if num in tutti_successivi:
                    rendimento[num] += 1

            migliori = sorted(gruppo_totale, key=lambda x: rendimento[x], reverse=True)[:n_giocare]

            # Numeri consigliati con stile più grande
            st.markdown("### 📌 Numeri consigliati da giocare:")
            consigliati_colorati = []
            for num in migliori:
                if num in numeri_base and num in tutti_successivi:
                    consigliati_colorati.append(f"<span style='color:green'><b>{num}</b></span>")
                elif num in successivi and num in tutti_successivi:
                    consigliati_colorati.append(f"<span style='color:orange'><b>{num}</b></span>")
                else:
                    consigliati_colorati.append(f"<span style='color:black'><b>{num}</b></span>")
            st.markdown(f"<p style='font-size:22px'>{', '.join(consigliati_colorati)}</p>", unsafe_allow_html=True)

            # Titolo + estratti base sotto, più grandi e neri
            st.markdown("### 🔁 Ripetizioni nei 5 turni successivi")
            st.markdown(f"<p style='font-size:17px; margin-top:-8px; color:black;'>Estratti base: <b>{', '.join(map(str, diretti))}</b></p>", unsafe_allow_html=True)

            col_estrazioni, col_legenda = st.columns([4, 1])
            with col_estrazioni:
                for riga in righe:
                    colorati = []
                    count_estratti = 0
                    for num in riga["Numeri usciti"]:
                        if num in diretti:
                            colorati.append(f"<span style='color:green'><b>{num}</b></span>")
                        elif num in successivi:
                            colorati.append(f"<span style='color:orange'><b>{num}</b></span>")
                        else:
                            colorati.append(f"<span style='color:black'>{num}</span>")
                        if num in migliori:
                            count_estratti += 1
                    # Etichetta A o T
                    etichetta = ""
                    if count_estratti >= 3:
                        etichetta = "<span style='color:red; font-size:22px;'><b>T</b></span>"
                    elif count_estratti == 2:
                        etichetta = "<span style='color:red; font-size:22px;'><b>A</b></span>"
                    line = f"🗓️ {riga['Data']} → Usciti: " + ", ".join(colorati) + f" {etichetta}"
                    st.markdown(line, unsafe_allow_html=True)

            with col_legenda:
                st.markdown("**Legenda**")
                st.markdown("<span style='color:green'><b>Verde</b></span>: Estratti base<br><span style='color:orange'><b>Arancione</b></span>: Precedenti/Successivi<br><span style='color:red; font-size:18px'><b>A</b></span>: Ambo<br><span style='color:red; font-size:18px'><b>T</b></span>: Terno", unsafe_allow_html=True)
