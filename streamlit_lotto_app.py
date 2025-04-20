def calcola_tecnica_lotto(terzo_bari, terzo_cagliari, giorno, mese, anno):
    """
    Calcola la tecnica del Lotto basata sui terzi estratti della prima estrazione del mese.
    
    Args:
        terzo_bari (int): Terzo estratto sulla ruota di Bari
        terzo_cagliari (int): Terzo estratto sulla ruota di Cagliari
        giorno (int): Giorno dell'estrazione
        mese (int): Mese dell'estrazione
        anno (int): Anno dell'estrazione
        
    Returns:
        dict: Dizionario contenente i risultati della tecnica
    """
    # Estrazione delle decine
    decina_bari = terzo_bari // 10
    decina_cagliari = terzo_cagliari // 10
    
    # Calcolo dell'ambata
    ambata = decina_bari + decina_cagliari
    
    # Se l'ambata è maggiore di 90 (il numero massimo del lotto), si sottrae 90
    if ambata > 90:
        ambata = ambata - 90
    
    # Creazione del dizionario dei risultati
    risultati = {
        "data_estrazione": f"{giorno:02d}/{mese:02d}/{anno}",
        "terzo_bari": terzo_bari,
        "terzo_cagliari": terzo_cagliari,
        "decina_bari": decina_bari,
        "decina_cagliari": decina_cagliari,
        "ambata": ambata,
        "ambi": f"{terzo_bari}-{terzo_cagliari}",
        "terna": f"{ambata}-{terzo_bari}-{terzo_cagliari}",
        "ruote_consigliate": ["Bari", "Cagliari", "Nazionale"]
    }
    
    return risultati

def mostra_risultati(risultati):
    """
    Mostra i risultati della tecnica in modo formattato.
    
    Args:
        risultati (dict): Dizionario contenente i risultati della tecnica
    """
    print("\n" + "=" * 50)
    print(f"TECNICA DEL LOTTO - Prima estrazione del {risultati['data_estrazione']}")
    print("=" * 50)
    print(f"\nTerzo estratto Bari: {risultati['terzo_bari']} (decina: {risultati['decina_bari']})")
    print(f"Terzo estratto Cagliari: {risultati['terzo_cagliari']} (decina: {risultati['decina_cagliari']})")
    print(f"\nAmbata: {risultati['ambata']} (derivante da {risultati['decina_bari']} + {risultati['decina_cagliari']})")
    print(f"Ambi da giocare: {risultati['ambi']}")
    print(f"Terna da giocare: {risultati['terna']}")
    print(f"\nRuote consigliate: {', '.join(risultati['ruote_consigliate'])}")
    print("\n" + "=" * 50)

def main():
    print("SISTEMA DI CALCOLO TECNICA DEL LOTTO")
    print("Basato sulla prima estrazione di ogni mese\n")
    
    try:
        # Input dei dati
        giorno = int(input("Inserisci il giorno dell'estrazione: "))
        mese = int(input("Inserisci il mese dell'estrazione (1-12): "))
        anno = int(input("Inserisci l'anno dell'estrazione: "))
        
        # Verifica se è la prima estrazione del mese
        if giorno > 8:
            print("\nATTENZIONE: Di solito la prima estrazione del mese cade nei primi 8 giorni.")
            conferma = input("Sei sicuro che questa sia la prima estrazione del mese? (s/n): ")
            if conferma.lower() != 's':
                print("Operazione annullata.")
                return
        
        terzo_bari = int(input("\nInserisci il terzo estratto della ruota di Bari: "))
        terzo_cagliari = int(input("Inserisci il terzo estratto della ruota di Cagliari: "))
        
        # Validazione dei numeri del lotto (1-90)
        if not (1 <= terzo_bari <= 90 and 1 <= terzo_cagliari <= 90):
            print("Errore: I numeri del lotto devono essere compresi tra 1 e 90.")
            return
            
        # Calcolo e visualizzazione dei risultati
        risultati = calcola_tecnica_lotto(terzo_bari, terzo_cagliari, giorno, mese, anno)
        mostra_risultati(risultati)
        
    except ValueError:
        print("Errore: Inserisci solo valori numerici validi.")
    
if __name__ == "__main__":
    main()
