
import streamlit as st
import pandas as pd

st.title("💰 Simulazione Gioco - Solo ultime 10 estrazioni (Ambo & Terno)")

uploaded_file = st.file_uploader("Carica il file CSV delle estrazioni", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file, skiprows=3)
    df["Data"] = pd.to_datetime(df["Data"], errors="coerce")

    ruota = st.selectbox("Scegli la ruota su cui simulare il gioco", [
        "Bari", "Cagliari", "Firenze", "Genova", "Milano",
        "Napoli", "Palermo", "Roma", "Torino", "Venezia", "Nazionale"
    ])

    st.success("File caricato correttamente!")

    spesa_per_colpo = st.number_input("Inserisci la spesa per ogni estrazione (es. 6.0)", min_value=1.0, value=6.0, step=0.5)

    tutte_date = sorted(df["Data"].dropna().unique())[-15:-5]  # Ultime 10 date utili (evita le ultime 5 senza estrazioni successive)
    bilancio_totale = 0
    risultati = []

    for data in tutte_date:
        row = df[df["Data"] == data]
        if row.empty:
            continue

        try:
            estratti = row[[ruota, f"{ruota}.1", f"{ruota}.2", f"{ruota}.3", f"{ruota}.4"]].iloc[0].tolist()
            estratti = [int(n) for n in estratti if pd.notnull(n)]
        except:
            continue

        # Calcola numeri precedenti e successivi
        diretti = estratti
        successivi = []
        for num in diretti:
            successivi.extend([
                num - 1 if num > 1 else 90,
                num + 1 if num < 90 else 1
            ])
        numeri_finali = sorted(set(diretti + successivi))

        vincita = 0
        esito = "❌ Nessuna vincita"
        estrazioni_giocate = 0

        # Simula le 5 estrazioni successive
        successive = df[df["Data"] > data].sort_values("Data").head(5)
        for _, r in successive.iterrows():
            estrazioni_giocate += 1
            numeri_estratti = [r[f"{ruota}"], r[f"{ruota}.1"], r[f"{ruota}.2"], r[f"{ruota}.3"], r[f"{ruota}.4"]]
            numeri_estratti = [int(n) for n in numeri_estratti if pd.notnull(n)]
            match = set(numeri_finali) & set(numeri_estratti)

            if len(match) >= 3:
                esito = "🎯 Terno"
                vincita = 4250
                break
            elif len(match) == 2:
                esito = "🔸 Ambo su 2"
                vincita = 250
                break
            elif len(match) == 3:
                esito = "🔹 Ambo su 3"
                vincita = 85
                break
            elif len(match) == 4:
                esito = "🟦 Ambo su 4"
                vincita = 41
                break

        spesa = estrazioni_giocate * spesa_per_colpo
        profitto = vincita - spesa
        bilancio_totale += profitto

        risultati.append({
            "Data": data.date(),
            "Estrazioni": estrazioni_giocate,
            "Esito": esito,
            "Vincita": f"{vincita:.2f} €",
            "Spesa": f"{spesa:.2f} €",
            "Profitto": f"{profitto:.2f} €",
            "Bilancio Totale": f"{bilancio_totale:.2f} €"
        })

    st.markdown("### 📊 Risultati della simulazione (ultime 10 date)")
    st.dataframe(pd.DataFrame(risultati))

    # RIEPILOGO FINALE
    df_risultati = pd.DataFrame(risultati)
    vincite = df_risultati[df_risultati["Esito"] != "❌ Nessuna vincita"].shape[0]
    perdite = df_risultati[df_risultati["Esito"] == "❌ Nessuna vincita"].shape[0]
    profitto_totale = df_risultati["Profitto"].apply(lambda x: float(x.replace("€", "").replace(",", "").strip())).sum()

    st.markdown("### 🧾 Riepilogo Finale")
    st.markdown(f"- ✅ **Vittorie:** {vincite}")
    st.markdown(f"- ❌ **Perdite:** {perdite}")
    st.markdown(f"- 💼 **Profitto Totale:** {profitto_totale:.2f} €")
