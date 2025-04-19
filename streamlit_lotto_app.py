import csv

def load_data_from_csv(file_path):
    """
    Carica i dati delle estrazioni del Lotto da un file CSV.

    Args:
        file_path (str): Il percorso del file CSV.

    Returns:
        dict: Un dizionario dove le chiavi sono i nomi delle ruote e i valori sono liste di numeri estratti.
              Restituisce None se si verifica un errore durante la lettura del file.
    """
    data = {}
    try:
        with open(file_path, 'r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            if reader.fieldnames:
                ruote = [field for field in reader.fieldnames if field != 'Estrazione'] # Assume 'Estrazione' o simili non è una ruota
                for ruota in ruote:
                    data[ruota] = [] # Inizializza la lista per ogni ruota

                for row in reader:
                    for ruota in ruote:
                        try:
                            numero = int(row[ruota])
                            data[ruota].append(numero)
                        except (ValueError, KeyError):
                            print(f"Attenzione: Valore non valido o colonna mancante per la ruota '{ruota}' nella riga {reader.line_num}. Riga saltata.")
                            break # Salta l'intera riga se c'è un problema in una colonna ruota
                return data
            else:
                print("Errore: Il file CSV è vuoto o non ha intestazioni.")
                return None
    except FileNotFoundError:
        print(f"Errore: File non trovato al percorso: {file_path}")
        return None
    except Exception as e:
        print(f"Errore durante la lettura del file CSV: {e}")
        return None

def analyze_number_frequency(data, numero_selezionato):
    """
    Analizza la frequenza di uscita del numero selezionato per ogni ruota.

    Args:
        data (dict): Il dizionario dei dati delle estrazioni, come restituito da load_data_from_csv.
        numero_selezionato (int): Il numero di interesse (tra 1 e 90).

    Returns:
        dict: Un dizionario dove le chiavi sono i nomi delle ruote e i valori sono le frequenze del numero.
    """
    frequenze = {}
    if not data:
        print("Nessun dato disponibile per l'analisi. Caricare prima i dati CSV.")
        return frequenze

    for ruota, numeri_estratti in data.items():
        conteggio = numeri_estratti.count(numero_selezionato)
        frequenza = conteggio / len(numeri_estratti) if numeri_estratti else 0  # Evita divisione per zero se lista vuota
        frequenze[ruota] = frequenza
    return frequenze

def suggest_optimal_wheel(frequenze):
    """
    Suggerisce la ruota con la frequenza più alta per il numero selezionato.

    Args:
        frequenze (dict): Il dizionario delle frequenze, come restituito da analyze_number_frequency.

    Returns:
        str: Il nome della ruota suggerita, oppure None se non ci sono dati validi.
    """
    if not frequenze:
        return None

    ruota_ottimale = None
    max_frequenza = -1

    for ruota, frequenza in frequenze.items():
        if frequenza > max_frequenza:
            max_frequenza = frequenza
            ruota_ottimale = ruota

    return ruota_ottimale

def display_results(frequenze, ruota_suggerita, numero_selezionato):
    """
    Visualizza i risultati dell'analisi sotto forma di tabella e suggerisce la ruota.

    Args:
        frequenze (dict): Il dizionario delle frequenze.
        ruota_suggerita (str): La ruota suggerita.
        numero_selezionato (int): Il numero analizzato.
    """
    print("\n--- Risultati Analisi Frequenze Lotto ---")
    print(f"Numero selezionato: {numero_selezionato}")
    print("\nFrequenze di uscita per ruota:")
    print("-" * 30)
    print("{:<15} {:<15}".format("Ruota", "Frequenza")) # Intestazioni tabella
    print("-" * 30)
    for ruota, frequenza in frequenze.items():
        print("{:<15} {:.2%}".format(ruota, frequenza)) # Formattazione output frequenza percentuale
    print("-" * 30)

    if ruota_suggerita:
        print(f"\nSuggerimento Ruota Ottimale: {ruota_suggerita}")
        print(f"Basato sull'analisi delle frequenze, la ruota di {ruota_suggerita} sembra essere la più 'logica' per giocare il numero {numero_selezionato}.")
    else:
        print("\nNessun suggerimento ruota disponibile. Dati insufficienti o nessun dato caricato.")

def main():
    """
    Funzione principale che gestisce il flusso del programma.
    """
    file_path = input("Inserisci il percorso del file CSV contenente le estrazioni del Lotto: ")
    numero_selezionato = 0
    while True:
        try:
            numero_selezionato = int(input("Inserisci il numero da analizzare (1-90): "))
            if 1 <= numero_selezionato <= 90:
                break
            else:
                print("Errore: Inserisci un numero compreso tra 1 e 90.")
        except ValueError:
            print("Errore: Inserisci un numero intero valido.")

    data_estrazioni = load_data_from_csv(file_path)

    if data_estrazioni:
        frequenze_ruote = analyze_number_frequency(data_estrazioni, numero_selezionato)
        if frequenze_ruote: # Verifica che ci siano frequenze calcolate prima di suggerire
            ruota_suggerita = suggest_optimal_wheel(frequenze_ruote)
            display_results(frequenze_ruote, ruota_suggerita, numero_selezionato)
        else:
            print("Nessuna frequenza calcolata. Impossibile suggerire una ruota.")
    else:
        print("Impossibile procedere con l'analisi a causa di errori nel caricamento dei dati.")

if __name__ == "__main__":
    main()