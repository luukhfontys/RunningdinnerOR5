import numpy as np
import matplotlib.pyplot as plt
import math as m
import pandas as pd
from Classes import Deelnemer, Huis
from Functions import ingest_deelnemers, ingest_huizen

file_path = 'Running Dinner dataset 2022.xlsx'
startoplossing_path = 'Running Dinner eerste oplossing 2022.xlsx'

deelnemers = ingest_deelnemers(file_path)

huizen = ingest_huizen(file_path)


#Start oplossing in dataframe zetten
df_startoplossing = pd.read_excel(startoplossing_path)

#voor hoofd, nagerecht bij deelnemers in de class zetten, en voorkeursgang in huis classes opslaan
for i in range(len(df_startoplossing)):
    
    deelnemers[df_startoplossing['Bewoner'][i]].voor = df_startoplossing['Voor'][i]
    deelnemers[df_startoplossing['Bewoner'][i]].hoofd = df_startoplossing['Hoofd'][i]
    deelnemers[df_startoplossing['Bewoner'][i]].na = df_startoplossing['Na'][i]
    huizen[df_startoplossing['Huisadres'][i]].voorbereidde_gang = df_startoplossing['kookt'][i]
    
    #Gasten per huis class gasten lijst vermelden
    for gang in ['Voor', 'Hoofd', 'Na']:
        huizen[df_startoplossing[gang][i]].gast_toevoeg(deelnemers[df_startoplossing['Bewoner'][i]].naam)
x=1