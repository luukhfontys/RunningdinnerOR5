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
    
    def gang_wissel(self, other, gang):
        setattr(self, gang, getattr(other, gang))
        setattr(other, gang, getattr(self, gang))
    
    def sync_attributen(self):
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
                    attribuut_strings.append(f"{key}: {value.naam}")  # Display the name of the linked Deelnemer
            else:
                attribuut_strings.append(f"{key}: {value}")
                
        return ", ".join(attribuut_strings)

class Huis:
    def __init__(self, adres, min_gasten, max_gasten):
        self.adres = adres
        self.min_gasten = min_gasten
        self.max_gasten = max_gasten
        self.gasten = []
        self.gang_voorkeur = None
        self.voorbereidde_gang = None
        
    def gast_toevoeg(self, gast: str):
        self.gasten.append(gast)
    
    @property
    def aantalgasten(self):
        return len(self.gasten)