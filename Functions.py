import pandas as pd
from Classes import Deelnemer, Huis, Oplossing

def ingest_deelnemers(file_path: str) -> dict:

    ## Deelnemer input waardes

    #Alle deelnemers in een dataframe zetten
    df_deelnemers = pd.read_excel(file_path, sheet_name = 'Bewoners')

    deelnemers = dict()

    # Voeg alles namen en adressen van deelnemers toe in dictionary van classes
    for index, row in df_deelnemers.iterrows():
        naam = row['Bewoner']
        adres = row['Huisadres']
        deelnemer = Deelnemer(naam, adres)
        deelnemers[deelnemer.naam] = deelnemer

    #Sla op wie er bij elkaar moet blijven
    df_bijelkaar = pd.read_excel(file_path, sheet_name = 'Paar blijft bij elkaar', skiprows=[0])

    for index, row in df_bijelkaar.iterrows():
        bewoner1 = deelnemers.get(row["Bewoner1"])
        bewoner2 = deelnemers.get(row["Bewoner2"])
        
        bewoner1.bijelkaarblijven = bewoner2
        bewoner2.bijelkaarblijven = bewoner1

    #Alle directe buren opslaan per deelnemer
    df_directe_buren = pd.read_excel(file_path, sheet_name = 'Buren', skiprows=[0])
    for i in range(len(df_directe_buren)):
        deelnemers[df_directe_buren.iloc[i, 0]].buren.append(deelnemers[df_directe_buren.iloc[i, 1]].naam)
    
    #Alle tafelgenoten van vorigjaar inladen
    df_tafelgenoten_vorigjaar = pd.read_excel(file_path, sheet_name = 'Tafelgenoot vorig jaar', skiprows=[0])
    for i in range(len(df_tafelgenoten_vorigjaar)):
        huidige_bewoner = df_tafelgenoten_vorigjaar['Bewoner1'][i]
        if deelnemers.get(huidige_bewoner) is not None:
            deelnemers[huidige_bewoner].tafelgenootvorigjaar.append(df_tafelgenoten_vorigjaar['Bewoner2'][i])

    #Alles naar set converten
    return deelnemers

def ingest_tafelgenoten_2_jaar_geleden(file_path: str, deelnemers: dict()) -> dict:
    df_tafel_genoten_2_jaar_geleden = pd.read_excel(file_path, sheet_name = 'Tafelgenoot vorig jaar', skiprows=[0])
    for i in range(len(df_tafel_genoten_2_jaar_geleden)):
        huidige_bewoner = df_tafel_genoten_2_jaar_geleden['Bewoner1'][i]
        if deelnemers.get(huidige_bewoner) is not None:
            deelnemers[huidige_bewoner].tafelgenoten2jaargeleden.append(df_tafel_genoten_2_jaar_geleden['Bewoner2'][i])
    return deelnemers
def ingest_huizen(file_path: str) -> dict:
    """Neemt de file path van xlsx en stopt alles in een dictionary van objecten"""
    
    #Input waardes voor huizen en deelnemers
    df_huizen = pd.read_excel(file_path, sheet_name = 'Adressen')
    df_deelnemers = pd.read_excel(file_path, sheet_name = 'Bewoners')
    df_kookte_vorig_jaar = pd.read_excel(file_path, sheet_name = 'Kookte vorig jaar', skiprows=[0])
    # df_huizen.dropna(subset= 'Min groepsgrootte',inplace=True)
    # df_huizen.reset_index(inplace=True,drop=True)

    huizen = dict()

    for index, row in df_huizen.iterrows():
        adres = row['Huisadres']
        min_gasten = row['Min groepsgrootte']
        max_gasten = row['Max groepsgrootte']
        gang_voorkeur = row['Voorkeur gang']
        
        #als er geen min of max aangegeven is vervang nan met 0
        if pd.isna(min_gasten):
            min_gasten = 0
            max_gasten = 0
        
        huis = Huis(adres, min_gasten, max_gasten)
        if not pd.isna(gang_voorkeur):
            huis.gang_voorkeur = gang_voorkeur
        huizen[huis.adres] = huis
    
    #bijhouden welke bewoners waar wonen en of ze vrijstelling van koken hebben of niet
    for index, row in df_deelnemers.iterrows():
        huizen[row['Huisadres']].bewoners.append(row['Bewoner'])
        
        if row['Kookt niet'] == 1:
            huizen[row['Huisadres']].kook_vrijstelling = True
    
    #alle gekookte gangen vorig jaar registreren bij behorende huisadres
    for index, row in df_kookte_vorig_jaar.iterrows():
        if huizen.get(row['Huisadres']) is not None:
            huizen[row['Huisadres']].kookte_vorigjaar = row['Gang']
    
    return huizen

def ingest_startoplossing(deelnemers: dict, huizen: dict, startoplossing_path: str) -> tuple[dict, dict]:
    
    #Start oplossing in dataframe zetten
    df_startoplossing = pd.read_excel(startoplossing_path)

    #voor hoofd, nagerecht bij deelnemers in de class zetten, en voorkeursgang in huis classes opslaan
    oplossing = Oplossing(deelnemers, huizen)
    for i in range(len(df_startoplossing)):
        oplossing.oplossing[
            df_startoplossing['Bewoner'][i]] = [df_startoplossing['kookt'][i],
                                                df_startoplossing['Voor'][i],
                                                df_startoplossing['Hoofd'][i],
                                                df_startoplossing['Na'][i],
                                                0]
        
        #Gasten per huis class gasten lijst vermelden
        # for gang in ['Voor', 'Hoofd', 'Na']:
        #     huizen[df_startoplossing[gang][i]].gast_toevoeg(deelnemers[df_startoplossing['Bewoner'][i]].naam)
    return oplossing