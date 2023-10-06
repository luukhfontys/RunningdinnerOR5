import numpy as np
import matplotlib.pyplot as plt
import math as m
import pandas as pd
import time
import copy
import random
from Classes import Deelnemer, Huis
from Functions import ingest_deelnemers, ingest_huizen, ingest_startoplossing, ingest_tafelgenoten_2_jaar_geleden

def Bereken_doelfunctie(oplossing: object):
    start = time.time()
    oplossing.Bereken_alle_wensen()
    eind = time.time()
    feasible = oplossing.feasible()
    Score = oplossing.doelfunctie
    return Score, feasible

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
    huis_adressen = [huis for huis in huizen]
    gangen = ['Voor', 'Hoofd', 'Na']
    
    start_oplossing.gang_kook_wissel('WO_79', 'VW_35')

    start_oplossing.gang_eet_wissel('WO_45_M_Die', 'WO_53_M_Ola', 'Voor')

    Score = Bereken_doelfunctie(start_oplossing)
    print(Score)

    
    
if __name__ == '__main__':
    main()