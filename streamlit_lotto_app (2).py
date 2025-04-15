# Selezione ruota e data
col1, col2 = st.columns(2)
with col1:
    ruota_input = st.selectbox("Scegli la ruota per calcolo base", ruote)
with col2:
    data_estrazione = st.date_input("Data estrazione", value=df["Data"].max().date())

# Funzione per ottenere i numeri estratti in una data su una ruota
def get_numeri_estrazione(data, ruota):
    row = df[df["Data"] == pd.Timestamp(data)]
    if row.empty:
        return []
    cols = [ruota, f"{ruota}.1", f"{ruota}.2", f"{ruota}.3", f"{ruota}.4"]
    numeri = row[cols].iloc[0].tolist()
    return [int(n) for n in numeri if pd.notnull(n)]

# Funzione per ottenere i numeri precedenti e successivi
def get_gruppo_numeri(numeri):
    gruppo = set()
    successivi = set()
    for num in numeri:
        successivi.update([
            num - 1 if num > 1 else 90,
            num + 1 if num < 90 else 1
        ])
    return sorted(numeri), sorted(successivi)

# Estrazione numeri e costruzione lista finale
numeri_base = get_numeri_estrazione(data_estrazione, ruota_input)
diretti, successivi = get_gruppo_numeri(numeri_base)
numeri_finali = sorted(set(diretti + successivi))
