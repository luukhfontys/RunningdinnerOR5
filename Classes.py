class Deelnemer:
    def __init__(self, naam, adres):
        self.naam = naam
        self.adres = adres
        self.voor = None
        self.hoofd = None
        self.na = None
        self.bijelkaarblijven = None
        self.buren = []
        
    def rooster(self):
        return [self.voor, self.hoofd, self.na]
    
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
    
    @property
    def drie_gangen_test(self): # 3 gangen per persoon ingeroosterd constraint.
        return None not in [self.voor, self.hoofd, self.na]
    
    @property #Feasibility voor hele class
    def deelnemer_feasible(self) -> bool:
        return all([self.drie_gangen_test])

class Huis:
    def __init__(self, adres, min_gasten, max_gasten):
        self.adres = adres
        self.min_gasten = min_gasten
        self.max_gasten = max_gasten
        self.gasten = []
        self.gang_voorkeur = None
        self.voorbereidde_gang = None
        self.bewoners = []
        self.kook_vrijstelling = False
        
    def gast_toevoeg(self, gast: str):
        self.gasten.append(gast)
    
    @property #Aantal gasten bijhouden
    def aantalgasten(self) -> int:
        return len(self.gasten)
    
    @property #max_gasten constraint
    def binnen_capaciteit(self) -> bool:
        return self.aantalgasten <= self.max_gasten
    
    @property #min_gasten constraint
    def minima_capaciteit_behaald(self) -> bool:
        return self.aantalgasten >= self.min_gasten
    
    @property #Bewoners koken op eigen adres constraint
    def bewoners_koken_thuis(self) -> bool:
        return all(bewoner in self.gasten for bewoner in self.bewoners)
    
    @property #Feasibility voor hele class
    def huis_feasible(self) -> bool:
        #Return True als feasible, of bij vrijstelling
        return all([self.binnen_capaciteit, self.minima_capaciteit_behaald, self.bewoners_koken_thuis]) or self.kook_vrijstelling