
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Estrazione Lotto - Numeri Finali", layout="centered")

st.title("🎯 Estrazione Lotto - Numeri Finali da Analizzare")

uploaded_file = st.file_uploader("Carica il file CSV delle estrazioni", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file, skiprows=3)
    df["Data"] = pd.to_datetime(df["Data"], errors="coerce")

    ruote = ["Bari", "Cagliari", "Firenze", "Genova", "Milano",
             "Napoli", "Palermo", "Roma", "Torino", "Venezia", "Nazionale"]

    st.success("File caricato correttamente!")

    ruota = st.selectbox("Scegli la ruota", ruote)
    data_estrazione = st.date_input("Scegli la data di estrazione", value=df["Data"].max().date())

    def get_numeri_estrazione(data, ruota):
        row = df[df["Data"] == pd.Timestamp(data)]
        if row.empty:
            return []
        cols = [ruota, f"{ruota}.1", f"{ruota}.2", f"{ruota}.3", f"{ruota}.4"]
        numeri = row[cols].iloc[0].tolist()
        return [int(n) for n in numeri if pd.notnull(n)]

    def get_gruppo_numeri(numeri):
        successivi = set()
        for num in numeri:
            successivi.update([
                num - 1 if num > 1 else 90,
                num + 1 if num < 90 else 1
            ])
        return sorted(numeri), sorted(successivi)

    numeri_base = get_numeri_estrazione(data_estrazione, ruota)
    diretti, successivi = get_gruppo_numeri(numeri_base)
    numeri_finali = sorted(set(diretti + successivi))

    st.markdown("## 🔎 Risultato Analisi")
    st.markdown(f"- **Ruota selezionata:** {ruota}")
    st.markdown(f"- **Data selezionata:** {data_estrazione.strftime('%d/%m/%Y')}")

    if numeri_base:
        st.markdown(f"- ✅ **Numeri estratti:** {', '.join(map(str, diretti))}")
        st.markdown(f"- 🔁 **Precedenti e successivi:** {', '.join(map(str, successivi))}")
        st.markdown(f"- 🎯 **Numeri finali da analizzare:** {', '.join(map(str, numeri_finali))}")
    else:
        st.warning("❗ Nessuna estrazione trovata per la data selezionata.")

    # 🔍 Controllo delle 5 estrazioni successive con evidenziazione finale
    st.markdown("## 🔁 Controllo delle 5 estrazioni successive")

    prossime = df[df["Data"] > pd.Timestamp(data_estrazione)].sort_values("Data").head(5)

    if prossime.empty:
        st.warning("Non ci sono estrazioni successive alla data selezionata.")
    else:
        for _, row in prossime.iterrows():
            estratti = [row[f"{ruota}"], row[f"{ruota}.1"], row[f"{ruota}.2"], row[f"{ruota}.3"], row[f"{ruota}.4"]]
            estratti = [int(n) for n in estratti if pd.notnull(n)]

            match = set(estratti) & set(numeri_finali)
            simbolo = ""
            if len(match) >= 3:
                simbolo = "🎯 <b>Terno</b>"
            elif len(match) == 2:
                simbolo = "🔸 <b>Ambo</b>"

            def format_num(n):
                if n in match:
                    if n in diretti:
                        return f"<span style='color:red; font-size:18px; font-weight:bold;'>{n}</span>"
                    elif n in successivi:
                        return f"<span style='color:green; font-size:18px; font-weight:bold;'>{n}</span>"
                return f"{n}"

            formatted_nums = [format_num(n) for n in estratti]
            st.markdown(f"🗓️ {row['Data'].date()} → " + ", ".join(formatted_nums) + f" {simbolo}", unsafe_allow_html=True)
