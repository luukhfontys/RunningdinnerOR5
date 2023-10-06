import numpy as np
import matplotlib.pyplot as plt
import math as m
import pandas as pd
import time
import copy
import random
import logging
import timeout_decorator
from timeout_decorator import timeout
from Classes import Deelnemer, Huis
from Functions import ingest_deelnemers, ingest_huizen, ingest_startoplossing, ingest_tafelgenoten_2_jaar_geleden



logger = logging.getLogger(name='2opt-logger')
logging.basicConfig(level=logging.DEBUG,
                    format='[%(asctime)s] %(message)s',
                    handlers=[logging.FileHandler("2-opt_debug.log")])

def export_oplossing(oplossing, Score):
    df_oplossing = pd.DataFrame.from_dict(oplossing.oplossing, orient='index')
    df_oplossing = df_oplossing.reset_index()
    df_oplossing.columns = ['Bewoner' , 'kookt', 'Voor', 'Hoofd', 'Na', 'aantal']
    df_oplossing.insert(4, 'kookt', df_oplossing.pop('kookt'))
    df_oplossing.insert(1, 'Huisadres', '')
    for i in range(len(df_oplossing['Bewoner'])):
        bewoner = df_oplossing['Bewoner'][i]
        adres = oplossing.deelnemers[bewoner].adres
        df_oplossing.at[i, 'Huisadres'] = adres
    df_oplossing.to_excel(f'oplossing optimized {Score[0]}.xlsx', index=True)
    
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



def main():
    timeout_tijd = 10 #seconden
    file_path = 'Running Dinner dataset 2023 v2.xlsx'
    file_path_vorigjaar = 'Running Dinner dataset 2022.xlsx'
    startoplossing_path = 'Running Dinner tweede oplossing 2023 v2.xlsx'

    #deelnemers in dictionary zetten
    deelnemers = ingest_deelnemers(file_path)
    #Data 2 jaar geleden laden
    deelnemers = ingest_tafelgenoten_2_jaar_geleden(file_path_vorigjaar, deelnemers)
    #Huizen in dictionary zetten
    huizen = ingest_huizen(file_path)

    #start oplossing invoeren bij deelnemers en huizen
    start_oplossing = ingest_startoplossing(deelnemers, huizen, startoplossing_path)

    
    deelnemer_namen = [deelnemer for deelnemer in deelnemers]
    #Hier worden huizen die vrijstelling hebben meteen eruit gefiltert
    huis_adressen = [huis for huis in huizen if not huizen[huis].kook_vrijstelling]
    gangen = ['Voor', 'Hoofd', 'Na']
    
    unieke_deelnemer_combinaties = generate_uniek(deelnemer_namen)
    unieke_huis_combinaties = generate_uniek(huis_adressen)
    
    stuck = False
    huidige_oplossing = start_oplossing
    while stuck == False:
        keuzegetal = random.choice(['eet_gang', 'kook_gang'])
        
        if keuzegetal == 'eet_gang':
            huidige_oplossing, improvedeet = eet_gang_optimizer(huidige_oplossing, unieke_deelnemer_combinaties, gangen, timeout_tijd)
            if improvedeet == False:
                logger.debug(msg=f"*eet_gang_optimizer* Timeout: {timeout_tijd}s trying kook_gang_optimizer")
                huidige_oplossing, improvedkook = kook_gang_optimizer(huidige_oplossing, unieke_huis_combinaties, timeout_tijd)
                if improvedkook == False:
                    logger.debug(msg=f"*kook_gang_optimizer* Timeout: {timeout_tijd}s Optimizer stopping ...")
                    stuck = True
        
        if keuzegetal == 'kook_gang':
            huidige_oplossing, improvedkook = kook_gang_optimizer(huidige_oplossing, unieke_huis_combinaties, timeout_tijd)
            if improvedkook == False:
                logger.debug(msg=f"*kook_gang_optimizer* Timeout: {timeout_tijd}s trying eet_gang_optimizer")
                huidige_oplossing, improvedeet = eet_gang_optimizer(huidige_oplossing, unieke_deelnemer_combinaties, gangen, timeout_tijd)
                if improvedeet == False:
                    logger.debug(msg=f"*eet_gang_optimize* Timeout: {timeout_tijd}s Optimizer stopping ...")
                    stuck = True
        
    
    Score = bereken_doelfunctie(huidige_oplossing)
    export_oplossing(huidige_oplossing, Score)
    print(Score)

    
    
if __name__ == '__main__':
    main()