import pandas as pd
import numpy as np

class deelnemer:
    def __init__(self, adres, naam):
        self.adres = adres
        self.naam = naam
        self.voor = ''
        self.hoofd = ''
        self.na = ''
        self.kennissen = []
        self.opties = []
        self.aantalopties = 0
        #### gaan we later toevoegen, hoort bij bewoner, kan ook via huis moeten we nog over nadenken
        #self.buren
        ####
        
    def rooster(self):
        return [self.voor,self.hoofd,self.na]
    
    def reset_opties(self):
        self.opties = []
        self.aantalopties = 0
        
    def add_optie(self, optie):
        self.opties.append(optie)
        self.aantalopties += 1
    
    def __lt__(self,other):
        return self.aantalopties < other.aantalopties 

    def verwachte_score(self,huis_gasten):
        mensen = []
        for huis in woningen:
            if huis.adres in self.rooster():
                mensen.extend(huis.gasten)
        while self.naam in mensen:
            mensen.remove(self.naam)
        return len(set(mensen).intersection(huis_gasten))
        
    def score(self):
        while self.naam in self.kennissen:
            self.kennissen.remove(self.naam)
        return len(set(self.kennissen))-len(self.kennissen)
    
    def scorev2(self):
        mensen = []
        for huis in woningen:
            if huis.adres in self.rooster():
                mensen.extend(huis.gasten)
        while self.naam in mensen:
            mensen.remove(self.naam)
        return len(set(mensen)) - len(mensen)

class woning:
    def __init__(self, adres, minzit, maxzit, voorkeur, gang=0):
        self.adres = adres
        self.gang = gang
        self.gasten = []
        self.minzit = minzit
        self.maxzit = maxzit
        self.voorkeur = voorkeur
        self.huisnummer =0
        
    def __lt__(self,other):
        return (self.maxzit - len(self.gasten)) < (other.maxzit - len(other.gasten))
        
    def nieuwe_gast(self, naam):
        if len(self.gasten) < self.maxzit:
            self.gasten.append(naam)
            return True
        else:
            return False
    def verwijder_gast(self, naam):
        if len(self.gasten) == self.minzit:
            return False
        else:
            self.gasten.pop(naam)
            return True
        
#frame met deelnemers: adres, naam
df_bewoners = pd.read_excel("Running Dinner dataset 2022.xlsx",sheet_name='Bewoners')
df_bewoners = df_bewoners.loc[:,('Bewoner','Huisadres')]

#frame met huizen: alleen adressen waar gekookt word, voorkeuren, zitplaatsen min en max
df_woning = pd.read_excel("Running Dinner dataset 2022.xlsx", sheet_name='Adressen')
df_woning.dropna(subset= 'Min groepsgrootte',inplace=True)
df_woning.reset_index(inplace=True,drop=True)

# maken van de deelnemers
bewoners = []
for i in df_bewoners.index:
    row = df_bewoners.iloc[i,:]
    naam = row[0]
    adres = row[1]
    bewoner = deelnemer(adres=adres,naam=naam)
    bewoners.append(bewoner)

# maken van de woningen
woningen = []
for i in df_woning.index:
    row = df_woning.iloc[i,:]
    adres = row[0]
    minzit = row[1]
    maxzit = row[2]
    voorkeur = row[3]
    huis = woning(adres=adres,minzit=minzit,maxzit=maxzit,voorkeur=voorkeur)
    woningen.append(huis)

# opstellen counter om aantal plaatsen per ronde bij te houden
aantal_plaatsen_per_ronde = [0,0,0]

aantal_locaties = [0,0,0]

#verdelen van de voorkeuren
for huis in woningen:
    if aantal_plaatsen_per_ronde[0] >= len(bewoners): #- aantal_locaties[0]:
        break
    elif huis.voorkeur != 'Voor':
        continue
    else:
        aantal_plaatsen_per_ronde[0] += huis.maxzit
        aantal_locaties[0]+=1
        huis.huisnummer = aantal_locaties[0]
        huis.gang = 'Voor'
# verdelen van de rest ( nog geen rekening gehouden met vorig jaar)
for huis in woningen:
    if aantal_plaatsen_per_ronde[0] >= len(bewoners): #- aantal_locaties[0]:
        print('ronde een is verdeeld')
        break
    elif type(huis.gang) == type(int()) and type(huis.voorkeur)!=type(str()):
        aantal_plaatsen_per_ronde[0] += huis.maxzit
        aantal_locaties[0]+=1
        huis.gang = 'Voor'
        huis.huisnummer = aantal_locaties[0]
    else:
        continue      

for huis in woningen:
    if aantal_plaatsen_per_ronde[1] >= len(bewoners): #- aantal_locaties[1]:
        break
    elif huis.voorkeur != 'Hoofd':
        continue
    else:
        aantal_plaatsen_per_ronde[1] += huis.maxzit
        aantal_locaties[1]+=1
        #print(aantal_locaties,huis.adres)
        huis.gang = 'Hoofd'
        huis.huisnummer = aantal_locaties[1]
# verdelen van de rest ( nog geen rekening gehouden met vorig jaar)
for huis in woningen:
    if aantal_plaatsen_per_ronde[1] >= len(bewoners): #- aantal_locaties[1]:
        print('ronde twee is verdeeld')
        break
    elif type(huis.gang) == type(int()) and type(huis.voorkeur)!=type(str()):
        aantal_plaatsen_per_ronde[1] += huis.maxzit
        aantal_locaties[1]+=1
        huis.gang = 'Hoofd'
        huis.huisnummer = aantal_locaties[1]
    else:
        continue 

for huis in woningen:
    if aantal_plaatsen_per_ronde[2] >= len(bewoners): #- aantal_locaties[2]:
        break
    elif huis.voorkeur != 'Na':
        continue
    else:
        aantal_plaatsen_per_ronde[2] += huis.maxzit
        aantal_locaties[2]+=1
        huis.gang = 'Na'
        huis.huisnummer = aantal_locaties[2]
# verdelen van de rest ( nog geen rekening gehouden met vorig jaar)
for huis in woningen:
    if aantal_plaatsen_per_ronde[2] >= len(bewoners): #- aantal_locaties[2]:
        print('ronde drie is verdeeld')
        break
    elif type(huis.gang) == type(int()) and type(huis.voorkeur)!=type(str()):
        aantal_plaatsen_per_ronde[2] += huis.maxzit
        aantal_locaties[2]+=1
        huis.gang = 'Na'
        huis.huisnummer = aantal_locaties[2]
    else:
        continue 


for huis in woningen:
    if type(huis.gang) != type(int()):
        #print(huis.gang)
        continue
    elif aantal_locaties[0] < 17:
        #print(huis.gang)
        huis.gang = 'Voor'
        aantal_locaties[0] += 1
    elif aantal_locaties[1] < 17:
        #print(huis.gang)
        huis.gang = 'Hoofd'
        aantal_locaties[1] += 1
    else:
        #print(huis.gang)
        huis.gang = 'Na'
        aantal_locaties[2] += 1
# nu is de capaciteit gezet, nu kunnen we mensen gaan indelen
aantal_plaatsen_per_ronde, aantal_locaties
# toewijzen van deelnemers
# alle mensen tijdens hun eigen gang toewijzen aan hun eigen huis
for huis in woningen:
    for bewoner in bewoners:
        if bewoner.adres != huis.adres:
            continue
        else:  
            huis.nieuwe_gast(bewoner.naam)
        if huis.gang == 'Voor':
            bewoner.voor = huis.adres
        elif huis.gang == 'Hoofd':
            bewoner.hoofd = huis.adres
        else:
            bewoner.na = huis.adres


# opsplitsen van de woningen
woningen_voor = []
woningen_hoofd = []
woningen_na = []
for huis in woningen:
    if huis.gang == 'Voor':
        woningen_voor.append(huis)
    elif huis.gang == 'Hoofd':
        woningen_hoofd.append(huis)
    else:
        woningen_na.append(huis)

# eerste ronde bewoners toekennen

##
# BELANGRIJK!! filteren op stellen, die komen elkaar ander namelijk later nog tegen
##

for bewoner in bewoners:
    while len(bewoner.voor) < 1:
        #print(bewoner.adres)
        huis = np.random.choice(woningen_voor)
        #print(huis.adres)
        score = bewoner.verwachte_score(huis.gasten)
        if score > 0:
            continue
        if huis.nieuwe_gast(bewoner.naam):
            bewoner.voor = huis.adres
###
# updaten kennissen lijst
###

for bewoner in bewoners:
    for huis in woningen_voor:
        if huis.adres == bewoner.voor:
            bewoner.kennissen.extend(huis.gasten)
####

# tweede ronde bewoners opties uitrekenen

###

for bewoner in bewoners:
    if len(bewoner.hoofd) != 0:
        continue
    for huis in woningen_hoofd:
        score = bewoner.verwachte_score(huis.gasten)
        if score == 0:
            bewoner.add_optie(huis)
        else:
            continue
minste_opties = 100
for bewoner in bewoners:
    #print(len(bewoner.opties))
    if len(bewoner.opties) == 0:
        continue
    elif bewoner.aantalopties < minste_opties:
        minste_opties = len(bewoner.opties)
print(minste_opties)

bewoners.sort()
    
######
# PLAN DE CAMPANGE

# sorteren op lengte van opties lijst, van laag naar hoog en dan indelen

# tweede voor selectie bij ronde drie, dan nog een keer doen
#####

###
for bewoner in bewoners:
    while len(bewoner.hoofd) < 1:
        #print(bewoner.adres)
        huis = np.random.choice(woningen_hoofd)
        score = bewoner.verwachte_score(huis.gasten)
        #print(score)
        if score > 0:
            continue
        #print(huis.adres)
        if huis.nieuwe_gast(bewoner.naam):
            bewoner.hoofd = huis.adres
###
# updaten kennissen lijst
###

for bewoner in bewoners:
    for huis in woningen_hoofd:
        if huis.adres == bewoner.hoofd:
            bewoner.kennissen.extend(huis.gasten)
###
#for bewoner in bewoners:
#    if bewoner.score() < 0:
#        print(bewoner.scorev2(), bewoner.naam)
# derde ronde bewoners toekennen
#
###
for bewoner in bewoners:
    bewoner.reset_opties()

#### opnieuw aantal opties uitrekenen:

for bewoner in bewoners:
    if len(bewoner.na) != 0:
        continue
    for huis in woningen_na:
        score = bewoner.verwachte_score(huis.gasten)
        if score == 0:
            bewoner.add_optie(huis)
        else:
            continue
            
##### aantal opties printen

minste_opties = 100
for bewoner in bewoners:
    if len(bewoner.opties) == 0:
        continue
    elif bewoner.aantalopties < minste_opties:
        minste_opties = len(bewoner.opties)
print(minste_opties)

bewoners.sort()

for bewoner in bewoners:
    while len(bewoner.na) < 1:
       #print(bewoner.adres)
        huis = np.random.choice(woningen_na)
        #print(huis.adres,huis.gasten)
        score = bewoner.verwachte_score(huis.gasten)
        #print(score)
        if score > 0:
            continue
        if huis.nieuwe_gast(bewoner.naam):
            bewoner.na = huis.adres
###
# updaten kennissen lijst
###

for bewoner in bewoners:
    for huis in woningen_na:
        if huis.adres == bewoner.na:
            bewoner.kennissen.extend(huis.gasten)
            
###

# herindelen huizen met te weinig gasten

woningen.sort()

lege_huizen = []
volle_huizen = []
for huis in woningen:
    if huis.minzit <= len(huis.gasten):
        continue
    lege_huizen.append(huis)
for huis in woningen:
    if huis.maxzit == len(huis.gasten):
        volle_huizen.append(huis)
        

###            
bewoners_after = {'Bewoner':[],'Huisadres':[],'Voor':[],'Hoofd':[],'Na':[]}
woning_after = {'Huisadres': [], 'kookt':[], 'aantal':[]}            
        
for bewoner in bewoners:
    bewoners_after['Bewoner'].append(bewoner.naam)
    bewoners_after['Huisadres'].append(bewoner.adres)
    bewoners_after['Voor'].append(bewoner.voor)
    bewoners_after['Hoofd'].append(bewoner.hoofd)
    bewoners_after['Na'].append(bewoner.na)

for huis in woningen:
    woning_after['Huisadres'].append(huis.adres)
    woning_after['kookt'].append(huis.gang)
    woning_after['aantal'].append(len(huis.gasten))
    
df_bewoners_after = pd.DataFrame(bewoners_after)
df_woning_after = pd.DataFrame(woning_after)

df_bewoners_after.set_index('Huisadres', drop=True, inplace=True)
df_woning_after.set_index('Huisadres', drop=True, inplace=True)
df_output = df_bewoners_after.join(df_woning_after,how='left')
df_output.reset_index(inplace=True)
columns_titles = ['Bewoner','Huisadres','Voor','Hoofd','Na','kookt','aantal']
df_output = df_output.reindex(columns=columns_titles,)
print(df_output)
df_output.to_excel('Oplossing.xlsx')    