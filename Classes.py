import numpy as np

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
        
    def gang_eet_wissel(self, deelnemer1: str, deelnemer2: str, gang: str):
        """"Deze functie wisselt 2 deelnemers van locatie voor een bepaalde gang."""
        #gangen opslaan voor beide
        gang1 = self.oplossing[deelnemer1][self.gangindex[gang]]
        gang2 = self.oplossing[deelnemer2][self.gangindex[gang]]
        
        #gangen wisselen
        self.oplossing[deelnemer1][self.gangindex[gang]] = gang2
        self.oplossing[deelnemer2][self.gangindex[gang]] = gang1
        
    def gang_kook_wissel(self, adres1: str, adres2: str):
        bewonersadres1 = self.huizen[adres1].bewoners
        bewonersadres2 = self.huizen[adres2].bewoners
        gang1 = self.oplossing[bewonersadres1[0]][0]
        gang2 = self.oplossing[bewonersadres2[0]][0]
        swap_bewoners = self.create_swap_map(bewonersadres1, bewonersadres2)
        
        swap_adres = {adres1: adres2, adres2: adres1} 
        
        swap_gangen = dict()
        for bewoner in bewonersadres1:
            swap_gangen[bewoner] = self.oplossing[swap_bewoners[bewoner]][self.gangindex[gang1]]
        for bewoner in bewonersadres2:
            swap_gangen[bewoner] = self.oplossing[swap_bewoners[bewoner]][self.gangindex[gang2]]
            
        for bewoner in bewonersadres1:
            self.oplossing[bewoner][self.gangindex[gang1]] = swap_gangen[bewoner]
        for bewoner in bewonersadres2:
            self.oplossing[bewoner][self.gangindex[gang2]] = swap_gangen[bewoner]
        
        #Eet gang overal omwisselen:
        for bewoner, oplossinglijst in self.oplossing.items():
            self.oplossing[bewoner] = [swap_adres.get(adres, adres) for adres in oplossinglijst]
        
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
    
    # Wens 1:
    @property
    def wens1(self):
        return self.gewichten[1] * self.Score_wens1 # <-inf, 0] range
    
    @property
    def wens2(self):
        return self.gewichten[2] * self.Score_wens2 # <-inf, 0] range
    
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
    
    def wens1_berekening(self): #Twee verschillende deelnemers zijn zo weinig mogelijk keer elkaars tafelgenoten; het liefstmaximaal één keer. Dit geldt zeker voor deelnemers uit hetzelfde huishouden.
        """Returned een dictionary met key='Deelnemer': [[Bewoners], [Aantal keer tafelgenoot per bewoner]]"""
        self.tafelgenoot_aantal = dict()
        self.Score_wens1 = 0
        for deelnemer1 in self.oplossing:
            self.tafelgenoot_aantal[deelnemer1] = [[], []]
            for deelnemer2 in self.oplossing:
                if deelnemer1 != deelnemer2:
                    tafel_overlap_set = set(self.oplossing[deelnemer1][1:4]).intersection(self.oplossing[deelnemer2][1:4])
                    overlap_count = len(tafel_overlap_set)
                    if overlap_count > 0:
                        self.tafelgenoot_aantal[deelnemer1][0].append(deelnemer2)
                        self.tafelgenoot_aantal[deelnemer1][1].append(overlap_count)
                        self.Score_wens1 -= overlap_count - 1
        return self.Score_wens1, self.tafelgenoot_aantal
    
    def wens2_berekening(self): #Een huishouden dat in 2022 een hoofdgerecht bereid heeft, bereidt tijdens de komende Running Dinner geen hoofdgerecht.
        """Returnt: (doel score wens 2, aantal keer waar wens2 wordt beschadigd, huizen waarbij dit gebeurt)"""
        self.huizen_hoofd_seq = []
        self.num_hoofd_seq = 0
        self.Score_wens2 = 0
        for huis in self.huizen:
            #verkrijg huidige kook gang
            huidige_kook_gang = self.oplossing[self.huizen[huis].bewoners[0]][0]
            if (self.huizen[huis].kookte_vorigjaar == 'Hoofd') and (huidige_kook_gang == 'Hoofd'):
                self.Score_wens2 -= 1
                self.huizen_hoofd_seq.append(huis)
        
        #Aantal huizen registreren waarbij hoofd gerecht 2 keer wordt gedaan achter elkaar
        self.num_hoofd_seq = abs(self.Score_wens2)
        return self.Score_wens2, self.num_hoofd_seq, self.huizen_hoofd_seq
    
    def wens3_berekening(self):
        self.Score_wens3 = 0
        #Huizen bijhouden waar voorkeur is toegekent
        self.huizen_voorkeur_gegeven_lijst = []
        for huis in self.huizen:
            Voorkeur_gang = self.huizen[huis].gang_voorkeur
            huidige_kook_gang = self.oplossing[self.huizen[huis].bewoners[0]][0]
            if (Voorkeur_gang != None) and (Voorkeur_gang == huidige_kook_gang):
                self.Score_wens3 += 1
                self.huizen_voorkeur_gegeven_lijst.append(huis)
        return self.Score_wens3, self.huizen_voorkeur_gegeven_lijst
    
    def wens4_berekening(self):
        self.Score_wens4 = 0
        self.tafelgenoot_vorigjaar_en_dit_jaar = dict()
        for deelnemer in self.oplossing:
            tafelgenootlijst_ditjaar = self.tafelgenoot_aantal[deelnemer][0]
            tafelgenootlijst_vorigjaar = self.deelnemers[deelnemer].tafelgenootvorigjaar
            if tafelgenootlijst_vorigjaar != []:
                intersect_lijst = set(tafelgenootlijst_ditjaar).intersection(tafelgenootlijst_vorigjaar)
                self.tafelgenoot_vorigjaar_en_dit_jaar[deelnemer] = intersect_lijst
                self.Score_wens4 -= len(intersect_lijst)
        
        return self.Score_wens4, self.tafelgenoot_vorigjaar_en_dit_jaar

    def wens5_berekening(self):  
        self.Score_wens5 = 0
        for deelnemer in self.oplossing:
            tafelgenoten = self.tafelgenoot_aantal[deelnemer][0]
            buren = self.deelnemers[deelnemer].buren
            tafel_overlap_set = set(tafelgenoten).intersection(buren)
            if len(tafel_overlap_set) > 0:
                
                self.Score_wens5 -= len(tafel_overlap_set)
                
        return self.Score_wens5
        
        
    def wens6_berekening(self):
        self.Score_wens6 = 0
        self.tafelgenoot_vorigjaar_en_2_jaar_geleden = dict()
        for deelnemer in self.oplossing:
            tafelgenootlijst_ditjaar = self.tafelgenoot_aantal[deelnemer][0]
            tafelgenootlijst_vorigjaar = self.deelnemers[deelnemer].tafelgenoten2jaargeleden
            if tafelgenootlijst_vorigjaar != []:
                intersect_lijst = set(tafelgenootlijst_ditjaar).intersection(tafelgenootlijst_vorigjaar)
                self.tafelgenoot_vorigjaar_en_2_jaar_geleden[deelnemer] = intersect_lijst
                self.Score_wens6 -= len(intersect_lijst)
    
        return self.Score_wens6, self.tafelgenoot_vorigjaar_en_2_jaar_geleden

    ## Overig
    @property
    def sync_attributen(self) -> bool: #Sychroniseerd bewoners die samen moeten blijven
        for deelnemer in self.oplossing:
            deelnemer1 = self.deelnemers[deelnemer]
            deelnemer2 = self.deelnemers[deelnemer].bijelkaarblijven
            if deelnemer2 is not None:
                self.oplossing[deelnemer2.naam][:4] = self.oplossing[deelnemer1.naam][:4]
    
    @property
    def update_aantalgasten(self):
        #reset value
        for deelnemer in self.oplossing:
            self.oplossing[deelnemer][4] = 0
        
        # re-count value
        for deelnemer in self.oplossing:
            for key, lijst in self.oplossing.items():
                self.oplossing[deelnemer][4] += lijst.count(self.deelnemers[deelnemer].adres)
    
    def create_swap_map(self, list1: list, list2: list):
        """
        Deze functie zorgt ervoor dat 2 mensen met 1 persoon van gangen kunnen wisselen door de
        twee personen allebei de locaties van de ene persoon te geven en het ene persoon de eerste
        van de 2 personen zijn locatie te geven.
        """
        swap_map = {}
        #lijst 1 is len(1) en list2 is len(2)
        if len(list1) == 1 and len(list2) > 1:
            for element in list2:
                swap_map[element] = list1[0]
                swap_map[list1[0]] = element
            #lijst 2 is len(1) en list2 is len(1)
        elif len(list2) == 1 and len(list1) > 1:
            for element in list1:
                swap_map[element] = list2[0]
                swap_map[list2[0]] = element
        else:
            #allebij even groot
            for i in range(len(list1)):
                swap_map[list1[i]] = list2[i]
                swap_map[list2[i]] = list1[i]

        return swap_map
    
    ##Feasibility checken
    @property
    def not_in_capacity(self) -> int:
        not_in_capacity_count = 0
        deelnemers_specifiek = []
        for deelnemer in self.oplossing:
            
            adres = self.deelnemers[deelnemer].adres
            min_gasten = self.huizen[adres].min_gasten
            max_gasten = self.huizen[adres].max_gasten
            #check of de deelnemer wel een aantal gasten binnen de aangeven waardes ontvangt
            if (self.oplossing[deelnemer][4] > max_gasten) or (self.oplossing[deelnemer][4] < min_gasten):
                not_in_capacity_count += 1
                deelnemers_specifiek.append(self.deelnemers[deelnemer].naam)
                
        return not_in_capacity_count, deelnemers_specifiek
    
    #check of bewoners niet koken op eigen adres (tenzij ze zijn vrijgesteld van koken)
    @property
    def kookt_niet_op_eigen_adres(self):
        kookt_niet_count = 0
        for deelnemer in self.oplossing:
            eigenadres = self.deelnemers[deelnemer].adres
            kookgang = self.oplossing[deelnemer][0]
            vrijstelling = self.huizen[eigenadres].kook_vrijstelling
            if not vrijstelling:
                if eigenadres != self.oplossing[deelnemer][self.gangindex[kookgang]]:
                    kookt_niet_count += 1
        return kookt_niet_count
    
    #Feasibility van huidige oplossing
    
    def feasible(self):
        #access property om aantal gasten te updaten
        self.update_aantalgasten
        self.kookt_niet_op_eigen_adres
        self.not_in_capacity
        self.sync_attributen
        return all([self.kookt_niet_op_eigen_adres + self.not_in_capacity[0] == 0])
    
class Deelnemer:
    def __init__(self, naam, adres):
        self.naam = naam
        self.adres = adres
        self.bijelkaarblijven = None
        self.buren = []
        self.tafelgenootvorigjaar = []
        self.tafelgenoten2jaargeleden = []
    
    def convert_lists_to_sets(self):
        # Convert the lists to sets
        self.buren = set(self.buren)
        self.tafelgenootvorigjaar = set(self.tafelgenootvorigjaar)
        self.tafelgenoten2jaargeleden = set(self.tafelgenoten2jaargeleden)
        
    def gang_wissel(self, other, gang): #Wissel gang tussen twee personen
        setattr(self, gang, getattr(other, gang))
        setattr(other, gang, getattr(self, gang))
    
    def sync_attributen(self) -> bool: #True if succesful False if not
        other = self.bijelkaarblijven
        if self.bijelkaarblijven is not None:
            other.voor = self.voor
            other.hoofd = self.hoofd
            other.na = self.na
            return True
        else:
            return False
        
    def __repr__(self) -> str:
        atributen = vars(self)
        attribuut_strings = []
        
        for key, value in atributen.items():
            if key == "bijelkaarblijven":
                if isinstance(value, Deelnemer):
                    attribuut_strings.append(f"{key}: {value.naam}")  # Display naam van Deelnemer
            else:
                attribuut_strings.append(f"{key}: {value}")
                
        return ", ".join(attribuut_strings)
    
    # @property
    # def drie_gangen_test(self): # 3 gangen per persoon ingeroosterd constraint.
    #     return None not in [self.voor, self.hoofd, self.na]
    
    # @property #Feasibility voor hele class
    # def deelnemer_feasible(self) -> bool:
    #     return all([self.drie_gangen_test])

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
        
    # def gast_toevoeg(self, gast: str):
    #     self.gasten.append(gast)
        
    # def gast_verwijder(self, gast: str):
    #     self.gasten.pop(gast)
        
    # @property #Aantal gasten bijhouden
    # def aantalgasten(self) -> int:
    #     return len(self.gasten)
    
    # @property #max_gasten constraint
    # def binnen_capaciteit(self) -> bool:
    #     return self.aantalgasten <= self.max_gasten
    
    # @property #min_gasten constraint
    # def minima_capaciteit_behaald(self) -> bool:
    #     return self.aantalgasten >= self.min_gasten
    
    # @property #Bewoners koken op eigen adres constraint
    # def bewoners_koken_thuis(self) -> bool:
    #     return all(bewoner in self.gasten for bewoner in self.bewoners)
    
    # @property #Feasibility voor hele class
    # def huis_feasible(self) -> bool:
    #     #Return True als feasible, of bij vrijstelling
    #     return all([self.binnen_capaciteit, self.minima_capaciteit_behaald, 
    #                 self.bewoners_koken_thuis]) or self.kook_vrijstelling