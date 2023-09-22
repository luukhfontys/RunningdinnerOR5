import pandas as pd
from Classes import Deelnemer, Huis

def ingest_deelnemers(file_path: str) -> dict:

    ## Deelnemer input waardes

    #Alle deelnemers in een dataframe zetten
    df_deelnemers = pd.read_excel('Running Dinner dataset 2022.xlsx', sheet_name = 'Bewoners')

    #Alle woningen waar gekookt wordt in een dataframe zetten
    df_woningen = pd.read_excel('Running Dinner dataset 2022.xlsx', sheet_name = 'Adressen')
    df_woningen.dropna(subset = 'Min groepsgrootte', inplace = True)
    df_woningen.reset_index(inplace = True, drop = True)

    deelnemers = dict()

    # Voeg alles namen en adressen van deelnemers toe in dictionary van classes
    for index, row in df_deelnemers.iterrows():
        naam = row['Bewoner']
        adres = row['Huisadres']
        deelnemer = Deelnemer(naam, adres)
        deelnemers[deelnemer.naam] = deelnemer

    #Sla op wie er bij elkaar moet blijven

    df_bijelkaar = pd.read_excel('Running Dinner dataset 2022.xlsx', sheet_name = 'Paar blijft bij elkaar', skiprows=[0])

    for index, row in df_bijelkaar.iterrows():
        bewoner1 = deelnemers.get(row["Bewoner1"])
        bewoner2 = deelnemers.get(row["Bewoner2"])
        
        bewoner1.bijelkaarblijven = bewoner2
        bewoner2.bijelkaarblijven = bewoner1

    #Alle directe buren opslaan per deelnemer
    df_directe_buren = pd.read_excel('Running Dinner dataset 2022.xlsx', sheet_name = 'Buren', skiprows=[0])
    for i in range(len(df_directe_buren)):
        deelnemers[df_directe_buren.iloc[i, 0]].buren.append(deelnemers[df_directe_buren.iloc[i, 1]])
    
    return deelnemers

def ingest_huizen(file_path: str) -> dict:
    """Neemt de file path van xlsx en stopt alles in een dictionary van objecten"""
    
    #Input waardes voor huizen
    df_huizen = pd.read_excel(file_path, sheet_name = 'Adressen')
    df_huizen.dropna(subset= 'Min groepsgrootte',inplace=True)
    df_huizen.reset_index(inplace=True,drop=True)

    huizen = dict()

    for index, row in df_huizen.iterrows():
        adres = row['Huisadres']
        min_gasten = row['Min groepsgrootte']
        max_gasten = row['Max groepsgrootte']
        gang_voorkeur = row['Voorkeur gang']

        huis = Huis(adres, min_gasten, max_gasten)
        if not pd.isna(gang_voorkeur):
            huis.gang_voorkeur = gang_voorkeur
        huizen[huis.adres] = huis
    return huizen