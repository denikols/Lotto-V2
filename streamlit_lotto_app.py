
import streamlit as st
import pandas as pd

st.title("📊 Analisi Completa - Ambi e Terni per Tutte le Ruote")

uploaded_file = st.file_uploader("Carica il file CSV delle estrazioni", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file, skiprows=3)
    df["Data"] = pd.to_datetime(df["Data"], errors="coerce")

    ruote = ["Bari", "Cagliari", "Firenze", "Genova", "Milano",
             "Napoli", "Palermo", "Roma", "Torino", "Venezia", "Nazionale"]

    st.success("File caricato correttamente!")

    analisi_data = []

    tutte_date = sorted(df["Data"].dropna().unique())

    for data in tutte_date:
        for ruota in ruote:
            row = df[df["Data"] == data]
            if row.empty:
                continue

            cols = [ruota, f"{ruota}.1", f"{ruota}.2", f"{ruota}.3", f"{ruota}.4"]
            try:
                estratti = row[cols].iloc[0].tolist()
                estratti = [int(n) for n in estratti if pd.notnull(n)]
            except:
                continue

            diretti = estratti
            successivi = []
            for num in diretti:
                successivi.append(num - 1 if num > 1 else 90)
                successivi.append(num + 1 if num < 90 else 1)
            numeri_finali = set(diretti + successivi)

            successive = df[df["Data"] > data].sort_values("Data").head(5)
            ambi = 0
            terni = 0

            for _, r in successive.iterrows():
                estratti_successivi = [r[f"{ruota}"], r[f"{ruota}.1"], r[f"{ruota}.2"], r[f"{ruota}.3"], r[f"{ruota}.4"]]
                estratti_successivi = [int(n) for n in estratti_successivi if pd.notnull(n)]
                match = set(estratti_successivi) & numeri_finali

                if len(match) >= 3:
                    terni += 1
                elif len(match) == 2:
                    ambi += 1

            analisi_data.append({
                "Ruota": ruota,
                "Ambi": ambi,
                "Terni": terni
            })

    df_analisi = pd.DataFrame(analisi_data)
    riepilogo = df_analisi.groupby("Ruota").sum().reset_index()
    riepilogo = riepilogo.sort_values(["Terni", "Ambi"], ascending=False)

    st.markdown("### 📋 Classifica Completa Ruote (Terni e Ambi Totali)")
    st.dataframe(riepilogo.reset_index(drop=True))
