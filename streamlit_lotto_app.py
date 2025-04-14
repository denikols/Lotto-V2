import pandas as pd
from collections import Counter
from datetime import timedelta

def get_numeri_estrazione(df, data, ruota):
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
    ruote = ["Bari", "Cagliari", "Firenze", "Genova", "Milano",
             "Napoli", "Palermo", "Roma", "Torino", "Venezia", "Nazionale"]
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

def suggerisci_per_ruota(df, ruota, num_top=5):
    """Suggerisce i migliori numeri da giocare per una ruota specifica."""
    cols = [ruota, f"{ruota}.1", f"{ruota}.2", f"{ruota}.3", f"{ruota}.4"]
    
    # Creiamo una lista di tutti i numeri estratti sulla ruota
    tutti_numeri = []
    for _, row in df.iterrows():
        estratti = [row[c] for c in cols if pd.notnull(row[c])]
        tutti_numeri.extend([int(n) for n in estratti])
    
    # Calcola frequenza
    conteggio = Counter(tutti_numeri)
    
    # Calcola ritardi
    ritardi = {}
    for num in range(1, 91):
        ultimo_estratto = None
        for _, row in df.sort_values("Data", ascending=False).iterrows():
            estratti = [int(row[c]) for c in cols if pd.notnull(row[c])]
            if num in estratti:
                ultimo_estratto = row["Data"]
                break
        
        if ultimo_estratto:
            ritardi[num] = (df["Data"].max() - ultimo_estratto).days
        else:
            ritardi[num] = 999  # Se mai estratto, alto ritardo

    # Calcola punteggio combinato (frequenza * 0.4 + ritardo * 0.6)
    punteggi = {}
    for num in range(1, 91):
        freq = conteggio.get(num, 0)
        rit = ritardi.get(num, 999)
        
        # Normalizza la frequenza (più è alta, meglio è)
        freq_norm = freq / max(conteggio.values()) if conteggio else 0
        
        # Normalizza il ritardo (più è alto, meglio è - perché è più probabile che esca)
        rit_norm = rit / max(ritardi.values()) if ritardi else 0
        
        punteggi[num] = freq_norm * 0.4 + rit_norm * 0.6
    
    # Ordina numeri per punteggio e restituisci i top
    numeri_ordinati = sorted(punteggi.items(), key=lambda x: x[1], reverse=True)
    return numeri_ordinati[:num_top]

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
        probabilita_ordinata = sorted(probabilita_successiva.items(), key=lambda item: item[1], reverse=True)[:5]  # Limita a 5 numeri
        return probabilita_ordinata
    else:
        return []