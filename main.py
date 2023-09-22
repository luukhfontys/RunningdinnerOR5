import numpy as np
import matplotlib.pyplot as plt
import math as m
import pandas as pd
from Classes import Deelnemer, Huis
from Functions import ingest_huizen

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
        

