import pandas as pd
import copy
import time
import random
import logging
from logger_utils import logger
from Classes import Deelnemer, Huis, Oplossing

logger = logging.getLogger(name='2opt-logger')

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

def bereken_doelfunctie(oplossing: object):
    oplossing.Bereken_alle_wensen()
    feasible = oplossing.feasible()
    Score = oplossing.doelfunctie
    return Score, feasible

def generate_uniek(lijst: list) -> list:
    """Genereert een lijst met all unieke combinaties waar volgorde niet uit maakt"""
    unieke_combinaties = []
    for i in range(len(lijst)):
        for j in range(i+1, len(lijst)):
            unieke_combinaties.append((lijst[i], lijst[j]))
    return unieke_combinaties

def eet_swap(oplossing: object, deelnemer1: str, deelnemer2: str, gang: str):
    nieuwe_oplossing = copy.deepcopy(oplossing)
    nieuwe_oplossing.gang_eet_wissel(deelnemer1, deelnemer2, gang)
    nieuwe_oplossing.sync_attributen
    return nieuwe_oplossing

def kook_swap(oplossing: object, adres1: str, adres2: str):
    nieuwe_oplossing = copy.deepcopy(oplossing)
    nieuwe_oplossing.gang_kook_wissel(adres1, adres2)
    nieuwe_oplossing.sync_attributen
    return nieuwe_oplossing

def export_oplossing(oplossing, Score, rekentijd_minuten):
    df_oplossing = pd.DataFrame.from_dict(oplossing.oplossing, orient='index')
    df_oplossing = df_oplossing.reset_index()
    df_oplossing.columns = ['Bewoner' , 'kookt', 'Voor', 'Hoofd', 'Na', 'aantal']
    df_oplossing.insert(4, 'kookt', df_oplossing.pop('kookt'))
    df_oplossing.insert(1, 'Huisadres', '')
    for i in range(len(df_oplossing['Bewoner'])):
        bewoner = df_oplossing['Bewoner'][i]
        adres = oplossing.deelnemers[bewoner].adres
        df_oplossing.at[i, 'Huisadres'] = adres
    df_oplossing.to_excel(f'Planning geoptimaliseerd, {Score[0]} {round(rekentijd_minuten, 1)}m.xlsx', index=True)

def eet_gang_optimizer(oplossing: object, unieke_deelnemer_combinaties: list, gangen: list, timeout_tijd: int) -> (object, bool):
    """
    This function optimizes a solution using a randomized approach.

    :param oplossing: The initial solution to be optimized.
    :param unieke_deelnemer_combinaties: List of unique participant combinations.
    :param gangen: List of gangs.
    :param timeout_tijd: timeout na deze duur.
    :return: The optimized solution and a boolean indicating if the solution was improved.
    """
    random.shuffle(unieke_deelnemer_combinaties)
    improved = False
    i = 0
    start_tijd = time.time()
    rekentijd = 0
    while not improved and (i < len(unieke_deelnemer_combinaties)) and (rekentijd < timeout_tijd):
        for gang in gangen:
            nieuwe_oplossing = eet_swap(oplossing, unieke_deelnemer_combinaties[i][0], unieke_deelnemer_combinaties[i][1], gang)
            scorenieuw, feasible = bereken_doelfunctie(nieuwe_oplossing)
            scorehuidig, _ = bereken_doelfunctie(oplossing)
            if (scorenieuw > scorehuidig) and feasible:
                logger.debug(msg=f"*eet_gang_optimizer* Bij iteratie: {i}, Nieuwe oplossing score van: {scorenieuw} > {scorehuidig}, {unieke_deelnemer_combinaties[i][0]} en {unieke_deelnemer_combinaties[i][1]} zijn hiervoor gewisselt.")
                improved = True
                return nieuwe_oplossing, improved
        i += 1
        huidige_tijd = time.time()
        rekentijd = huidige_tijd - start_tijd
    return oplossing, improved

def kook_gang_optimizer(oplossing: object, unieke_huis_combinaties: list, timeout_tijd: int) -> (object, bool):
    random.shuffle(unieke_huis_combinaties)
    improved = False
    i = 0
    start_tijd = time.time()
    rekentijd = 0
    while not improved and (i < len(unieke_huis_combinaties)) and (rekentijd < timeout_tijd):
        nieuwe_oplossing = kook_swap(oplossing, unieke_huis_combinaties[i][0], unieke_huis_combinaties[i][1])
        scorenieuw, feasible = bereken_doelfunctie(nieuwe_oplossing)
        scorehuidig, _ = bereken_doelfunctie(oplossing)
        if (scorenieuw > scorehuidig) and feasible:
            logger.debug(msg=f"*kook_gang_optimizer* Bij iteratie: {i}, Nieuwe oplossing score van: {scorenieuw} > {scorehuidig}, {unieke_huis_combinaties[i][0]} en {unieke_huis_combinaties[i][1]} zijn hiervoor gewisselt.")
            improved = True
            return nieuwe_oplossing, improved
        i += 1
        huidige_tijd = time.time()
        rekentijd = huidige_tijd - start_tijd
    return oplossing, improved