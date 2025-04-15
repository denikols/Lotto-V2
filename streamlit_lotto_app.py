
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
