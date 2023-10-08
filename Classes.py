import pandas as pd

class Oplossing:
    def __init__(self, deelnemers: dict, huizen: dict):
        self.oplossing = dict() # key= 'Naam', items= [gang, voor, hoofd, na, aantalgasten]
        self.deelnemers = deelnemers
        self.huizen = huizen
        self.gangindex = {'Voor': 1, 'Hoofd': 2, 'Na': 3}
        self.gewichten = {1: 6, 
                          2: 5,
                          3: 4,
                          4: 3,
                          5: 2,
                          6: 1}
        self.Score_wens1 = 0
        self.tafelgenoot_aantal = dict()
        
        self.Score_wens2 = 0
        self.num_hoofd_seq = 0
        self.huizen_hoofd_seq = []
        
        self.Score_wens3 = 0
        self.huizen_voorkeur_gegeven_lijst = []
        
        self.Score_wens4 = 0
        self.tafelgenoot_vorigjaar_en_dit_jaar = dict()
        
        self.Score_wens5 = 0
        
        self.Score_wens6 = 0
        self.tafelgenoot_vorigjaar_en_2_jaar_geleden = dict()
        
    def gang_eet_wissel(self, deelnemer1: str, deelnemer2: str, gang: str) -> None:
        """"
        Wisselt de eetgangen tussen twee deelnemers voor de opgegeven gang.
        
        Parameters:
            deelnemer1 (str): De naam van de eerste deelnemer.
            deelnemer2 (str): De naam van de tweede deelnemer.
            gang (str): De naam van de eetgang waarin de deelnemers worden gewisseld.

        Opmerkingen:
            Deze methode past de oplossing direct aan en past de interne waardes aan van het Oplossing-object.
            
        Returns:
            None
        """
        
        #gangen opslaan voor beide
        gang1 = self.oplossing[deelnemer1][self.gangindex[gang]]
        gang2 = self.oplossing[deelnemer2][self.gangindex[gang]]
        
        #gangen wisselen
        self.oplossing[deelnemer1][self.gangindex[gang]] = gang2
        self.oplossing[deelnemer2][self.gangindex[gang]] = gang1
        
    def gang_kook_wissel(self, adres1: str, adres2: str) -> None:
        """
        Wisselt de kookgangen tussen twee huizen en past de oplossing aan.

        Parameters:
            adres1 (str): Het adres van het eerste huis.
            adres2 (str): Het adres van het tweede huis.

        Opmerkingen:
            Deze methode wisselt de kookgangen tussen de twee opgegeven huizen en past de oplossing direct aan.
            Het verwisselt de kookgangen van alle bewoners in de huizen en update de interne staat van het Oplossing-object.
            De gang die het huishouden niet meer hoeft te koken wordt vervolgens vervangen met de gang waar het andere huis
            oorspronkelijk die gang ging eten en vice versa.
            
        Werking:
            >>> gang_kook_wissel('W_77', 'W_55')
            
            Voorbeeld planning:
            Adres   Voor    Hoofd   Na
            W_77:  [W_22,   W_33,   W_77]
            W_55:  [W_11,   W_55,   W_88]
            
            Planning na wissel:
            Adres   Voor    Hoofd   Na
            W_77:  [W_22,   W_77,   W_88]
            W_55:  [W_11,   W_33,   W_55]
            
            Dus:W_77 maakt Na -> Hoofd
                W_55 maakt Hoofd -> Na
                W_77 Na -> W_88
                W_55 Hoofd -> W_33
            
            En dat voor alle bewoners met adres W_77 en W_55. 
            Uit de bewoners wordt door create_swap_map() gekozen wie met wie de verloren eet gangen precies wisselt.
            
        Returns:
            None
        """
        
        #Bewonerslijst van beide huizen verkrijgen
        bewonersadres1 = self.huizen[adres1].bewoners
        bewonersadres2 = self.huizen[adres2].bewoners
        
        #Huidige kookgangen van de bewoners verkrijgen
        gang1 = self.oplossing[bewonersadres1[0]][0]
        gang2 = self.oplossing[bewonersadres2[0]][0]
        
        #Swap-mapping voor bewoners tussen de huizen maken
        swap_bewoners = self.create_swap_map(bewonersadres1, bewonersadres2)
        
        #Swap-mapping voor de huizen
        swap_adres = {adres1: adres2, adres2: adres1}
        
        #Gangwisseling voor de bewoners van beide huizen registreren in swap_gangen
        swap_gangen = dict()
        for bewoner in bewonersadres1:
            swap_gangen[bewoner] = self.oplossing[swap_bewoners[bewoner]][self.gangindex[gang1]]
        for bewoner in bewonersadres2:
            swap_gangen[bewoner] = self.oplossing[swap_bewoners[bewoner]][self.gangindex[gang2]]

        #De eetgangen van alle bewoners aanpassen volgens de swap_gangen
        for bewoner in bewonersadres1:
            self.oplossing[bewoner][self.gangindex[gang1]] = swap_gangen[bewoner]
        for bewoner in bewonersadres2:
            self.oplossing[bewoner][self.gangindex[gang2]] = swap_gangen[bewoner]
        
        #Eet gang overal omwisselen:
        for bewoner, oplossinglijst in self.oplossing.items():
            self.oplossing[bewoner] = [swap_adres.get(adres, adres) for adres in oplossinglijst]
        
        #Eigen kook gang wisselen
        for bewoner in bewonersadres1:
            self.oplossing[bewoner][0] = gang2
            self.oplossing[bewoner][self.gangindex[gang2]] = adres1
        
        for bewoner in bewonersadres2:
            self.oplossing[bewoner][0] = gang1
            self.oplossing[bewoner][self.gangindex[gang1]] = adres2
    
    
    ## Doel functie berekeningen
    @property
    def doelfunctie(self): #Maximalisatie is het doeleind
        return self.wens1 + self.wens2 + self.wens3 + self.wens4 + self.wens5 + self.wens6
    
    ## Pas gewichten toe op alle wens scores en sla ze op in een uiteindelijke eigen score.
    @property
    def wens1(self):
        return self.gewichten[1] * self.Score_wens1
    
    @property
    def wens2(self):
        return self.gewichten[2] * self.Score_wens2 
    
    @property
    def wens3(self):
        return self.gewichten[3] * self.Score_wens3

    @property
    def wens4(self):
        return self.gewichten[4] * self.Score_wens4
    
    @property
    def wens5(self):
        return self.gewichten[5] * self.Score_wens5
    
    @property
    def wens6(self):
        return self.gewichten[6] * self.Score_wens6
    
    #Om alle wensen uit te rekenen
    def Bereken_alle_wensen(self):
        self.wens1_berekening()
        self.wens2_berekening()
        self.wens3_berekening()
        self.wens4_berekening()
        self.wens5_berekening()
        self.wens6_berekening()
    
    ##Wens berekeningen

    def wens1_berekening(self) -> (int, dict):
        """
        Bereken de score en tafelgenootinformatie volgens Wens 1.

        Wens 1: Twee verschillende deelnemers zijn zo weinig mogelijk keer elkaars tafelgenoten; het liefst maximaal één keer.
                Dit geldt zeker voor deelnemers uit hetzelfde huishouden.

        Returns:
            tuple: Een tuple bestaande uit de score volgens Wens 1 en een dictionary met tafelgenootinformatie.
                De dictionary heeft de volgende structuur:
                - Key: Deelnemer
                - Value: Een lijst met twee elementen:
                    - Lijst van bewoners die deelnemer's tafelgenoot zijn.
                    - Lijst van het aantal keer dat de bewoners tafelgenoot zijn geweest.

        Opmerkingen:
            Deze methode berekent de score en verzamelt tafelgenootinformatie volgens Wens 1.
            De score wordt bepaald op basis van hoe vaak deelnemers dezelfde tafelgenoten hebben.
            De tafelgenootinformatie wordt opgeslagen in een dictionary met deelnemers als keys
            en lijsten van bewoners en tafelgenootaantallen als items.
        """
        
        #initialise waardes
        self.tafelgenoot_aantal = dict()
        self.Score_wens1 = 0
        
        for deelnemer1 in self.oplossing:
            self.tafelgenoot_aantal[deelnemer1] = [[], []]
            for deelnemer2 in self.oplossing:
                if deelnemer1 != deelnemer2:
                    
                    # Bereken het aantal gemeenschappelijke tafelgenoten tussen deelnemer1 en deelnemer2.
                    tafel_overlap_set = set(self.oplossing[deelnemer1][1:4]).intersection(self.oplossing[deelnemer2][1:4])
                    overlap_count = len(tafel_overlap_set)
                    if overlap_count > 0:
                        
                        # Voeg deelnemer2 en het aantal keer dat ze tafelgenoten zijn toe aan de tafelgenootinformatie van deelnemer1, en de naam met wie ze tafelgenoot zijn.
                        self.tafelgenoot_aantal[deelnemer1][0].append(deelnemer2)
                        self.tafelgenoot_aantal[deelnemer1][1].append(overlap_count)
                        
                        #Checkt of deelnemers bij elkaar moeten blijven, zo ja dan wordt er niet gestraft omdat ze bij elkaar zitten.
                        if self.deelnemers[deelnemer1].bijelkaarblijven is None:
                            #Update de totale score volgens Wens 1.
                            self.Score_wens1 -= overlap_count - 1
                        elif self.deelnemers[deelnemer1].bijelkaarblijven.naam != deelnemer2:
                            #Update de totale score volgens Wens 1.
                            self.Score_wens1 -= overlap_count - 1
                        
        return self.Score_wens1, self.tafelgenoot_aantal
    
    def wens2_berekening(self) -> (int, list):
        """
        Bereken de score en informatie volgens Wens 2.

        Wens 2: Een huishouden dat in 2022 een hoofdgerecht bereid heeft, bereidt tijdens de komende Running Dinner geen hoofdgerecht.

        Returns:
            tuple: Een tuple bestaande uit de doelscore voor Wens 2, het aantal keer waarin Wens 2 wordt beschadigt, en
                een lijst van huizen waarbij deze schending optreedt.

        Opmerkingen:
            Deze methode berekent de score en verzamelt informatie volgens Wens 2.
            De doelscore voor Wens 2 is het aantal huishoudens dat in 2022 een hoofdgerecht bereidde en nu weer een hoofdgerecht moet bereiden.
            Het aantal keer waarin Wens 2 wordt beschadigt, wordt ook geregistreerd, evenals de huizen waarbij deze schending optreedt.
        """
        
        #initialise waardes
        self.huizen_hoofd_seq = []
        self.num_hoofd_seq = 0
        self.Score_wens2 = 0
        
        for huis in self.huizen:
            #verkrijg huidige kook gang van het huis
            huidige_kook_gang = self.oplossing[self.huizen[huis].bewoners[0]][0]
            if (self.huizen[huis].kookte_vorigjaar == 'Hoofd') and (huidige_kook_gang == 'Hoofd'):
                # Als het huis in 2022 een hoofdgerecht bereidde en nu weer een hoofdgerecht moet bereiden, verlaag de score.
                self.Score_wens2 -= 1
                self.huizen_hoofd_seq.append(huis)
        
        # Registreer het aantal huishoudens waarbij het hoofdgerecht twee keer achter elkaar wordt bereid.
        self.num_hoofd_seq = abs(self.Score_wens2)
        
        return self.Score_wens2, self.num_hoofd_seq, self.huizen_hoofd_seq
    
    def wens3_berekening(self) -> (int, list):
        """
        Bereken de score en informatie volgens Wens 3.

        Wens 3: Indien mogelijk wordt er rekening gehouden met een door de gastheer of -vrouw opgegeven voorkeursgang.

        Returns:
            tuple: Een tuple bestaande uit de doelscore voor Wens 3 en een lijst van huizen waarbij aan deze wens is voldaan.

        Opmerkingen:
            Deze methode berekent de score en verzamelt informatie volgens Wens 3.
            De doelscore voor Wens 3 is het aantal huizen waarbij aan de voorkeursgang van de gastheer of -vrouw is voldaan.
            Een lijst van huizen waarbij aan deze wens is voldaan, wordt ook verzameld.
        """
        #initialiseer waardes
        self.Score_wens3 = 0
        #Huizen bijhouden waar voorkeur is toegekent
        self.huizen_voorkeur_gegeven_lijst = []
        for huis in self.huizen:
            
            #Verkrijg voorkeurs gang van huis
            Voorkeur_gang = self.huizen[huis].gang_voorkeur
            
            #verkijg kook gang die huis momenteel moet maken
            huidige_kook_gang = self.oplossing[self.huizen[huis].bewoners[0]][0]
            
            if (Voorkeur_gang != None) and (Voorkeur_gang == huidige_kook_gang):
                # Als de voorkeursgang is opgegeven en overeenkomt met de huidige kookgang, verhoog de score.
                self.Score_wens3 += 1
                self.huizen_voorkeur_gegeven_lijst.append(huis)
        return self.Score_wens3, self.huizen_voorkeur_gegeven_lijst
    
    def wens4_berekening(self) -> (int, dict): # Twee deelnemers die in 2022 bij elkaar aan tafel zaten, zijn in 2023 liefst niet elkaars tafelgenoot.
        """
        Bereken de score en informatie volgens Wens 4.

        Wens 4: Twee deelnemers die in 2022 bij elkaar aan tafel zaten, zijn in 2023 liefst niet elkaars tafelgenoot.

        Returns:
            tuple: Een tuple bestaande uit de doelscore voor Wens 4 en een dictionary met deelnemers die vorig jaar en dit jaar elkaars tafelgenoot zijn.

        Opmerkingen:
            Deze methode berekent de score en verzamelt informatie volgens Wens 4.
            De doelscore voor Wens 4 is het aantal keren dat deelnemers die vorig jaar en dit jaar elkaars tafelgenoot zijn, voorkomen.
            Een dictionary wordt gemaakt waarbij de keys deelnemers zijn en de items de lijst van deelnemers zijn die vorig jaar en dit jaar elkaars tafelgenoot zijn.
        """
        
        #initialiseer waardes
        self.Score_wens4 = 0
        self.tafelgenoot_vorigjaar_en_dit_jaar = dict()
        
        
        for deelnemer in self.oplossing:
            
            #Verkrijg tafelgenoten dit jaar en van vorig jaar
            tafelgenootlijst_ditjaar = self.tafelgenoot_aantal[deelnemer][0]
            tafelgenootlijst_vorigjaar = self.deelnemers[deelnemer].tafelgenootvorigjaar
            
            #Check of persoon vorig jaar mee deet.
            if tafelgenootlijst_vorigjaar != []:
                #Check of personen al tafelgenoot zijn geweest
                intersect_lijst = set(tafelgenootlijst_ditjaar).intersection(tafelgenootlijst_vorigjaar)
                
                #Registreer in aparte attribute
                self.tafelgenoot_vorigjaar_en_dit_jaar[deelnemer] = intersect_lijst
                
                #Aantal keer dat ze nog een keer tafelgenoot zijn geweest aftrekken van wens 4 score
                self.Score_wens4 -= len(intersect_lijst)
        
        return self.Score_wens4, self.tafelgenoot_vorigjaar_en_dit_jaar

    def wens5_berekening(self) -> int: #Twee tafelgenoten zijn bij voorkeur niet elkaars directe buren.
        """
        Bereken de score volgens Wens 5.

        Wens 5: Twee tafelgenoten zijn bij voorkeur niet elkaars directe buren.

        Returns:
            int: De score voor Wens 5.

        Opmerkingen:
            De score wordt verminderd voor elk paar tafelgenoten dat ook directe buren van elkaar is.
        """
        
        #initialiseer waardes
        self.Score_wens5 = 0
        
        for deelnemer in self.oplossing:
            #verkijg tafelgenoten dit jaar
            tafelgenoten = self.tafelgenoot_aantal[deelnemer][0]
            
            #verkrijg buren van huidige deelnemer
            buren = self.deelnemers[deelnemer].buren
            
            #Check of er buren in de tafelgenoten staan van de huidige deelnemer
            tafel_overlap_set = set(tafelgenoten).intersection(buren)
            
            #Zo ja, trek het aantal keer dat buren tafelgenoten zijn van de huidige deelnemer af van de wens 5 score
            if len(tafel_overlap_set) > 0:
                self.Score_wens5 -= len(tafel_overlap_set)
                
        return self.Score_wens5
        
        
    def wens6_berekening(self) -> (int, dict):
        """
        Bereken de score volgens Wens 6.

        Wens 6: Twee deelnemers die in 2021 bij elkaar aan tafel zaten, zijn in 2023 liefst niet elkaars tafelgenoot.

        Returns:
            tuple: Een tuple bestaande uit de score van wens 6, en een dictionary met voor alle deelnemers een lijst
                   met alle deelenemers die 2 jaar geleden ook al tafelgenoten waren met een bepaalde deelnemer.

        Opmerkingen:
            De score wordt verminderd voor elk paar deelnemers dat in 2021 bij elkaar aan tafel zat en ook in 2023 tafelgenoten is.
        """
        
        #initialiseer waardes
        self.Score_wens6 = 0
        self.tafelgenoot_vorigjaar_en_2_jaar_geleden = dict()
        
        for deelnemer in self.oplossing:
            
            #verkrijg tafelgenoten dit jaar en van 2 jaar geleden
            tafelgenootlijst_ditjaar = self.tafelgenoot_aantal[deelnemer][0]
            tafelgenootlijst_2jaargeleden = self.deelnemers[deelnemer].tafelgenoten2jaargeleden
            
            #Check of deelnemer 2 jaar geleden ook mee deet.
            if tafelgenootlijst_2jaargeleden != []:
                
                #Check of er tafelgenoten van 2 jaar geleden in de tafelgenoten staan van de huidige deelnemer
                intersect_lijst = set(tafelgenootlijst_ditjaar).intersection(tafelgenootlijst_2jaargeleden)
                
                #Registreer intersect lijst.
                self.tafelgenoot_vorigjaar_en_2_jaar_geleden[deelnemer] = intersect_lijst
                
                #Trek het aantal keer dat deelnemer en tafelgenoot 2 jaar geleden ook al samen zaten af van de wens 6 score
                self.Score_wens6 -= len(intersect_lijst)
    
        return self.Score_wens6, self.tafelgenoot_vorigjaar_en_2_jaar_geleden

    ## Overig
    @property
    def sync_attributen(self) -> None:
        """
        Deze property synchroniseert bewoners die samen moeten blijven door hun eet en kook gang attributen gelijk te maken.

        Returns:
            None

        Opmerkingen:
            Deze property controleert of er bewoners zijn die samen moeten blijven (aangegeven door 'bijelkaarblijven').
            Als er bewoners zijn die samen moeten blijven, worden hun eerste vier attributen gelijk gemaakt om ze samen te houden.
        """
        
        for deelnemer in self.oplossing:
            deelnemer1 = self.deelnemers[deelnemer]
            deelnemer2 = self.deelnemers[deelnemer].bijelkaarblijven
            
            # Controleer of er een bewoner is om mee te synchroniseren
            if deelnemer2 is not None:
                # Synchroniseer de kook en eet gang attributen van beide bewoners
                self.oplossing[deelnemer2.naam][:4] = self.oplossing[deelnemer1.naam][:4]
    
    @property
    def update_aantalgasten(self):
        """Deze property reset eerst de waarde van het aantal gasten voor elke bewoner en berekent daarna deze waarde opnieuw."""
        #reset waarde aantal gasten naar 0 voor elke deelnemer
        for deelnemer in self.oplossing:
            self.oplossing[deelnemer][4] = 0
        
        #Bereken waarde opnieuw
        for deelnemer in self.oplossing:
            for key, lijst in self.oplossing.items():
                # Tel hoe vaak de adreswaarde van de bewoner voorkomt in de lijsten van andere bewoners
                self.oplossing[deelnemer][4] += lijst.count(self.deelnemers[deelnemer].adres)
    
    def totaal_aantal_voorkeuren_huishouden(self):
        """Deze property berekent het totaal aantal voorkeuren aangegeven door elk huis."""
        totaal_aantal_voorkeuren_huishouden = 0
        for huis in self.huizen:
            if self.huizen[huis].gang_voorkeur is not None:
                totaal_aantal_voorkeuren_huishouden += 1
        return totaal_aantal_voorkeuren_huishouden

    def create_swap_map(self, bewonersadres1: list, bewonersadres2: list) -> dict:
        """
        Deze functie zorgt ervoor dat 2 mensen met 1 persoon van gangen kunnen wisselen door de
        twee personen allebei de locaties van de ene persoon te geven en het ene persoon de eerste
        van de 2 personen zijn locatie te geven.
        
        Parameters:
            bewonersadres1: lijst van bewoners van huis1 met lengte 1 of 2
            bewonersadres2: lijst van bewoners van huis2 met lengte 1 of 2
            
        Returns:
            dict: Een dictionary die aangeeft welke personen van huis 1 moeten wisselen met personen van huis 2.
        """
        
        swap_map = {}
        # Als lijst 1 één persoon bevat en lijst 2 meerdere personen bevat
        if len(bewonersadres1) == 1 and len(bewonersadres2) > 1:
            for element in bewonersadres2:
                swap_map[element] = bewonersadres1[0]
                swap_map[bewonersadres1[0]] = element
            # Als lijst 2 één persoon bevat en lijst 1 meerdere personen bevat
        elif len(bewonersadres2) == 1 and len(bewonersadres1) > 1:
            for element in bewonersadres1:
                swap_map[element] = bewonersadres2[0]
                swap_map[bewonersadres2[0]] = element
        else:
            # Beide lijsten hebben evenveel personen, één-op-één wisseling
            for i in range(len(bewonersadres1)):
                swap_map[bewonersadres1[i]] = bewonersadres2[i]
                swap_map[bewonersadres2[i]] = bewonersadres1[i]

        return swap_map
    
    @property
    def not_in_capacity(self) -> (int, list):
        """
        Deze property telt het aantal bewoners dat niet binnen de capaciteitslimieten van hun huis valt en geeft hun namen terug.

        Returns:
            tuple: Een tuple bestaande uit het aantal bewoners dat niet binnen de capaciteitslimieten valt en een lijst met hun namen.
        """
        not_in_capacity_count = 0
        deelnemers_specifiek = []
        for deelnemer in self.oplossing:
            adres = self.deelnemers[deelnemer].adres
            min_gasten = self.huizen[adres].min_gasten
            max_gasten = self.huizen[adres].max_gasten
            #check of de deelnemer wel een aantal gasten binnen de aangeven waardes ontvangt
            if (self.oplossing[deelnemer][4] > max_gasten) or (self.oplossing[deelnemer][4] < min_gasten):
                #Zo ja, registreer dat het niet binnen de waardes zit, en bij wie het gebeurt is.
                not_in_capacity_count += 1
                deelnemers_specifiek.append(self.deelnemers[deelnemer].naam)
                
        return not_in_capacity_count, deelnemers_specifiek
    
    #check of bewoners niet koken op eigen adres (tenzij ze zijn vrijgesteld van koken)
    @property
    def kookt_niet_op_eigen_adres(self) -> int:
        """
        Deze property controleert of bewoners niet koken op hun eigen adres, tenzij ze zijn vrijgesteld van koken.

        Returns:
            int: Het aantal bewoners dat niet op hun eigen adres kookt, tenzij ze zijn vrijgesteld.
        """
        
        kookt_niet_count = 0
        
        for deelnemer in self.oplossing:
            eigenadres = self.deelnemers[deelnemer].adres
            kookgang = self.oplossing[deelnemer][0]
            vrijstelling = self.huizen[eigenadres].kook_vrijstelling
            
            # Controleer of de bewoner vrijgesteld is van koken
            if not vrijstelling:
                
                # Controleer of de bewoner kookt op zijn eigen adres
                try:
                    if eigenadres != self.oplossing[deelnemer][self.gangindex[kookgang]]:
                        kookt_niet_count += 1
                except KeyError as e:
                    print(f'Persoon zonder vrijstelling: {deelnemer} kookt niet -> kookgang: {e}')
                    
        return kookt_niet_count
    
    @property
    def aantal_personen_niet_ingedeeld(self):
        aantal_personen_niet_ingedeeld = 0
        
        for deelnemer in self.oplossing:
            if pd.isna(self.oplossing[deelnemer][1:4]).any():
                aantal_personen_niet_ingedeeld += 1
        return aantal_personen_niet_ingedeeld
    
    @property
    def aantal_personen_dat_niet_kookt_maar_wel_moet(self):
        aantal_personen_dat_niet_kookt_maar_wel_moet = 0
        for deelnemer in self.oplossing:
            kookgang = self.oplossing[deelnemer][0]
            vrijgesteld = self.huizen[self.deelnemers[deelnemer].adres].kook_vrijstelling
            if pd.isna(kookgang) and not vrijgesteld:
                aantal_personen_dat_niet_kookt_maar_wel_moet += 1
        return aantal_personen_dat_niet_kookt_maar_wel_moet
    
    @property
    def aantal_personen_dat_bijelkaar_moet_blijven_maar_dit_niet_zijn(self):
        aantal_personen_dat_bijelkaar_moet_blijven_maar_dit_niet_zijn = 0
        for deelnemer in self.oplossing:
            if self.deelnemers[deelnemer].bijelkaarblijven is not None:
                if not self.oplossing[deelnemer][1:4] == self.oplossing[self.deelnemers[deelnemer].bijelkaarblijven.naam][1:4]:
                    aantal_personen_dat_bijelkaar_moet_blijven_maar_dit_niet_zijn += 1
        return aantal_personen_dat_bijelkaar_moet_blijven_maar_dit_niet_zijn
    
    #Feasibility van huidige oplossing
    
    def feasible(self):
        """
        Controleer of de huidige oplossing haalbaar is op basis van verschillende criteria.

        Returns:
            bool: True als de oplossing haalbaar is, anders False.

        Opmerkingen:
            Deze functie controleert de haalbaarheid van de huidige oplossing op basis van verschillende criteria.
            Het roept de relevante property-methoden aan om de benodigde informatie bij te werken en te controleren:
            - 'update_aantalgasten': update het aantal gasten per bewoner.
            - 'kookt_niet_op_eigen_adres': controleer of bewoners niet op hun eigen adres koken, tenzij ze zijn vrijgesteld.
            - 'not_in_capacity': controleer of bewoners binnen de capaciteitslimieten van hun huis vallen.
            - 'sync_attributen': synchroniseer bewoners die samen moeten blijven.

            De functie retourneert True als aan alle haalbaarheidscriteria is voldaan, anders retourneert het False.
        """
        #Roep de relevante property-methoden aan om informatie bij te werken en te controleren
        self.sync_attributen
        self.update_aantalgasten
        self.kookt_niet_op_eigen_adres
        self.not_in_capacity
        self.aantal_personen_niet_ingedeeld
        self.aantal_personen_dat_niet_kookt_maar_wel_moet
        self.aantal_personen_dat_bijelkaar_moet_blijven_maar_dit_niet_zijn
        
        #Controleer of er geen overtredingen zijn (koken op eigen adres en capaciteit)
        return all([self.kookt_niet_op_eigen_adres + self.not_in_capacity[0] == 0])
    
class Deelnemer:
    def __init__(self, naam, adres):
        self.naam = naam
        self.adres = adres
        self.bijelkaarblijven = None
        self.buren = []
        self.tafelgenootvorigjaar = []
        self.tafelgenoten2jaargeleden = []

class Huis:
    def __init__(self, adres, min_gasten, max_gasten):
        self.adres = adres
        self.min_gasten = min_gasten
        self.max_gasten = max_gasten
        self.gang_voorkeur = None
        self.voorbereidde_gang = None
        self.bewoners = []
        self.kook_vrijstelling = False
        self.kookte_vorigjaar = None