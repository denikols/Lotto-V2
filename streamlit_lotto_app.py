# Script semplificato per la tecnica del Lotto

def main():
    print("SISTEMA DI CALCOLO TECNICA DEL LOTTO")
    print("Basato sulla prima estrazione di ogni mese\n")
    
    try:
        # Input dei dati
        giorno = int(input("Inserisci il giorno dell'estrazione: "))
        mese = int(input("Inserisci il mese dell'estrazione (1-12): "))
        anno = int(input("Inserisci l'anno dell'estrazione: "))
        
        terzo_bari = int(input("\nInserisci il terzo estratto della ruota di Bari: "))
        terzo_cagliari = int(input("Inserisci il terzo estratto della ruota di Cagliari: "))
        
        # Validazione dei numeri del lotto (1-90)
        if not (1 <= terzo_bari <= 90 and 1 <= terzo_cagliari <= 90):
            print("Errore: I numeri del lotto devono essere compresi tra 1 e 90.")
            return
        
        # Estrazione delle decine
        decina_bari = terzo_bari // 10
        decina_cagliari = terzo_cagliari // 10
        
        # Calcolo dell'ambata
        ambata = decina_bari + decina_cagliari
        
        # Se l'ambata è maggiore di 90 (il numero massimo del lotto), si sottrae 90
        if ambata > 90:
            ambata = ambata - 90
        
        # Mostra risultati
        print("\n" + "=" * 50)
        print(f"TECNICA DEL LOTTO - Prima estrazione del {giorno:02d}/{mese:02d}/{anno}")
        print("=" * 50)
        print(f"\nTerzo estratto Bari: {terzo_bari} (decina: {decina_bari})")
        print(f"Terzo estratto Cagliari: {terzo_cagliari} (decina: {decina_cagliari})")
        print(f"\nAmbata: {ambata} (derivante da {decina_bari} + {decina_cagliari})")
        print(f"Ambi da giocare: {terzo_bari}-{terzo_cagliari}")
        print(f"Terna da giocare: {ambata}-{terzo_bari}-{terzo_cagliari}")
        print(f"\nRuote consigliate: Bari, Cagliari, Nazionale")
        print("\n" + "=" * 50)
        
        # Mantieni aperta la finestra del terminale
        input("\nPremi INVIO per terminare il programma...")
            
    except ValueError:
        print("Errore: Inserisci solo valori numerici validi.")
        input("\nPremi INVIO per terminare il programma...")

if __name__ == "__main__":
    main()
