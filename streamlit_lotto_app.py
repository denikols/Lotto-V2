
import streamlit as st
import pandas as pd

st.title("📅 Visualizzatore Estrazioni Lotto")

df = pd.read_csv("/mnt/data/24e25.csv", skiprows=3)
df["Data"] = pd.to_datetime(df["Data"], errors="coerce")
df = df.dropna(subset=["Data"])
df = df.sort_values("Data", ascending=False)

ruote = ["Bari", "Cagliari", "Firenze", "Genova", "Milano",
         "Napoli", "Palermo", "Roma", "Torino", "Venezia", "Nazionale"]

date_uniche = df["Data"].dt.date.unique()
data_scelta = st.selectbox("Scegli una data di estrazione", date_uniche)

estrazione = df[df["Data"].dt.date == data_scelta]

if estrazione.empty:
    st.warning("Nessuna estrazione trovata.")
else:
    dati = {}

    dati["Bari"] = estrazione[['Bari', 'Bari.1', 'Bari.2', 'Bari.3', 'Bari.4']].values.tolist()[0]
    
    dati["Cagliari"] = estrazione[['Cagliari', 'Cagliari.1', 'Cagliari.2', 'Cagliari.3', 'Cagliari.4']].values.tolist()[0]
    
    dati["Firenze"] = estrazione[['Firenze', 'Firenze.1', 'Firenze.2', 'Firenze.3', 'Firenze.4']].values.tolist()[0]
    
    dati["Genova"] = estrazione[['Genova', 'Genova.1', 'Genova.2', 'Genova.3', 'Genova.4']].values.tolist()[0]
    
    dati["Milano"] = estrazione[['Milano', 'Milano.1', 'Milano.2', 'Milano.3', 'Milano.4']].values.tolist()[0]
    
    dati["Napoli"] = estrazione[['Napoli', 'Napoli.1', 'Napoli.2', 'Napoli.3', 'Napoli.4']].values.tolist()[0]
    
    dati["Palermo"] = estrazione[['Palermo', 'Palermo.1', 'Palermo.2', 'Palermo.3', 'Palermo.4']].values.tolist()[0]
    
    dati["Roma"] = estrazione[['Roma', 'Roma.1', 'Roma.2', 'Roma.3', 'Roma.4']].values.tolist()[0]
    
    dati["Torino"] = estrazione[['Torino', 'Torino.1', 'Torino.2', 'Torino.3', 'Torino.4']].values.tolist()[0]
    
    dati["Venezia"] = estrazione[['Venezia', 'Venezia.1', 'Venezia.2', 'Venezia.3', 'Venezia.4']].values.tolist()[0]
    
    dati["Nazionale"] = estrazione[['Nazionale', 'Nazionale.1', 'Nazionale.2', 'Nazionale.3', 'Nazionale.4']].values.tolist()[0]
    
    st.markdown("### 🎯 Numeri estratti")
    df_tabella = pd.DataFrame(dati, index=["Numeri"])
    st.dataframe(df_tabella.transpose())
