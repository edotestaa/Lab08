from database import prezzo_DAO
from database.distributore_DAO import DistributoreDAO
from database.prezzo_DAO import PrezzoDAO
'''
    MODELLO:
    - Rappresenta la struttura dati
    - Si occupa di gestire lo stato dell'applicazione
    - Interagisce con il database
'''

class Model:
    def __init__(self):
        self._distributori = None
        self.load_distributori()

        self.__sequenza_ottima = []
        self.__costo_ottimo = -1

    def load_distributori(self):
        """ Carica tutti i distributori e li setta nella variabile self._distributori """
        self._distributori = DistributoreDAO.get_distributori()

    def get_prezzo_medio(self, mese:int):
        """
        Calcola, per ogni distributore, il prezzo medio al litro per il mese selezionato.
        :param mese: Mese selezionato (un intero da 1 a 12)
        :return: lista di tuple --> (nome del distributore, media), es. (Distributore A, 1.789)
        """
        return PrezzoDAO.get_prezzo_medio_per_distributore(mese)

    def get_sequenza_ottima(self, mese:int):
        """
        Calcola la sequenza ottimale di rifornimenti nei primi 7 giorni
        :return: sequenza di nomi distributore ottimale
        :return: costo ottimale (cioè quello minimizzato dalla sequenza scelta)
        """
        self.__sequenza_ottima = []
        self.__costo_ottimo = -1
        prezzi_settimana = self.__get_prezzi_prima_settimana_mese(mese)

        self.__ricorsione([], 1, None, 0, prezzi_settimana)


        id_to_nome = {distributore.id: distributore.nome for distributore in self._distributori}
        sequenza_nomi = [f"Giorno {giorno}: {id_to_nome[i]}" for giorno, i in enumerate(self.__sequenza_ottima, start=1)]
        return sequenza_nomi, round(self.__costo_ottimo, 2)

    def __ricorsione(self, sequenza_parziale, giorno, ultimo_distributore, costo_corrente, prezzi_settimana):
        """ Implementa la ricorsione """
        if giorno > 7:
            if self.__costo_ottimo == -1 or costo_corrente < self.__costo_ottimo:
                self.__costo_ottimo = costo_corrente
                self.__sequenza_ottima = list(sequenza_parziale)
            return

        if self.__costo_ottimo != -1:
            if costo_corrente >= self.__costo_ottimo:
                return

        for id_distributore, lista_prezzi in prezzi_settimana.items():

            prezzo_giorno = lista_prezzi[giorno - 1]
            costo_rifornimento = prezzo_giorno * 100
            if ultimo_distributore is not None and ultimo_distributore != id_distributore:
                costo_spostamento = 5.0
            else:
                costo_spostamento = 0.0

            nuovo_costo = costo_corrente + costo_rifornimento + costo_spostamento

            sequenza_parziale.append(id_distributore)

            self.__ricorsione(
                sequenza_parziale,
                giorno + 1,
                id_distributore,
                nuovo_costo,
                prezzi_settimana
            )
            sequenza_parziale.pop()

    def __get_prezzi_prima_settimana_mese(self, mese: int):
        """
        Restituisce i prezzi dei primi 7 giorni del mese selezionato per ciascun distributore.
        :return: un dizionario: {id_distributore: [prezzo_giorno1, ..., prezzo_giorno7]}
        """
        prezzi_settimana = {}

        for distributore in self._distributori:
            prezzi = distributore.get_prezzi()
            prezzi_filtrati = []


            for p in prezzi:
                if p.data.month == mese:
                    if p.data.day >= 1 and p.data.day <= 7:
                        prezzi_filtrati.append(p)

            lista_prezzi_ordinati = []
            for giorno in range(1, 8):
                for p in prezzi_filtrati:
                    if p.data.day == giorno:
                        lista_prezzi_ordinati.append(p.prezzo_litro)

            prezzi_settimana[distributore.id] = lista_prezzi_ordinati

        return prezzi_settimana