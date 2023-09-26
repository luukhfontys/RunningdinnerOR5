class Oplossing:
    def __init__(self, deelnemers: dict, huizen: dict):
        self.oplossing = dict() # key= 'Naam', items= [gang, voor, hoofd, na, aantalgasten]
        self.deelnemers = deelnemers
        self.huizen = huizen
    
    def gang_kook_wissel(self, adres1: str, adres2: str):
        gangindex = {
            'Voor'    : 1,
            'Hoofd'   : 2,
            'Na'      : 3}
        bewonersadres1 = self.huizen[adres1].bewoners
        bewonersadres2 = self.huizen[adres2].bewoners
        gang1 = self.oplossing[bewonersadres1[0]][0]
        gang2 = self.oplossing[bewonersadres2[0]][0]
        swap_bewoners = self.create_swap_map(bewonersadres1, bewonersadres2)
        
        swap_adres = {adres1: adres2, adres2: adres1} 
        
        swap_gangen = dict()
        for bewoner in bewonersadres1:
            swap_gangen[bewoner] = self.oplossing[swap_bewoners[bewoner]][gangindex[gang1]]
        for bewoner in bewonersadres2:
            swap_gangen[bewoner] = self.oplossing[swap_bewoners[bewoner]][gangindex[gang2]]
            
        for bewoner in bewonersadres1:
            self.oplossing[bewoner][gangindex[gang1]] = swap_gangen[bewoner]
        for bewoner in bewonersadres2:
            self.oplossing[bewoner][gangindex[gang2]] = swap_gangen[bewoner]
        
        #Eet gang overal omwisselen:
        for bewoner, oplossinglijst in self.oplossing.items():
            self.oplossing[bewoner] = [swap_adres.get(adres, adres) for adres in oplossinglijst]
        
        for bewoner in bewonersadres1:
            self.oplossing[bewoner][0] = gang2
            self.oplossing[bewoner][gangindex[gang2]] = adres1
        
        for bewoner in bewonersadres2:
            self.oplossing[bewoner][0] = gang1
            self.oplossing[bewoner][gangindex[gang1]] = adres2
        
    def create_swap_map(self, list1, list2):
            swap_map = {}
            #lijst 1 is 1 en list2 is 2
            if len(list1) == 1 and len(list2) > 1:
                for element in list2:
                    swap_map[element] = list1[0]
                    swap_map[list1[0]] = element
                #lijst 2 is 1 en list2 is 1
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

    @property
    def sync_attributen(self) -> bool: #Sychroniseerd bewoners die samen moeten blijven
        for deelnemer in self.oplossing:
            deelnemer1 = self.deelnemers[deelnemer]
            deelnemer2 = self.deelnemers[deelnemer].bijelkaarblijven            
            if deelnemer2 is not None:
                self.oplossing[deelnemer2.naam] = self.oplossing[deelnemer1.naam]
    
    @property
    def update_aantalgasten(self):
        #reset value
        for deelnemer in self.oplossing:
            self.oplossing[deelnemer][4] = 0
        
        # re-count value
        for deelnemer in self.oplossing:
            for key, lijst in self.oplossing.items():
                self.oplossing[deelnemer][4] += lijst.count(self.deelnemers[deelnemer].adres)
    
    #Check how many are in capacity
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
        gangindex = {
            'Voor'    : 1,
            'Hoofd'   : 2,
            'Na'      : 3}
        kookt_niet_count = 0
        for deelnemer in self.oplossing:
            eigenadres = self.deelnemers[deelnemer].adres
            kookgang = self.oplossing[deelnemer][0]
            vrijstelling = self.huizen[eigenadres].kook_vrijstelling
            if not vrijstelling:
                if eigenadres != self.oplossing[deelnemer][gangindex[kookgang]]:
                    kookt_niet_count += 1
        return kookt_niet_count
    
    #Feasibility van huidige oplossing
    @property
    def feasible(self):
        return all([self.kookt_niet_op_eigen_adres + self.not_in_capacity == 0])
    
class Deelnemer:
    def __init__(self, naam, adres):
        self.naam = naam
        self.adres = adres
        self.bijelkaarblijven = None
        self.buren = []
    
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
        
    def gast_toevoeg(self, gast: str):
        self.gasten.append(gast)
        
    def gast_verwijder(self, gast: str):
        self.gasten.pop(gast)
        
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