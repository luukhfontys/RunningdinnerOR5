import numpy as np
import matplotlib.pyplot as plt
import math as m
import pandas as pd
import time
from Classes import Deelnemer, Huis
from Functions import ingest_deelnemers, ingest_huizen, ingest_startoplossing, ingest_tafelgenoten_2_jaar_geleden

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

# start_oplossing.update_aantalgasten()

#Check of start oplossing feasible is.
# start_feasible = check_feasible(deelnemers, huizen)
# start_oplossing.gang_kook_wissel('WO_79', 'VW_35')

# start_oplossing.gang_eet_wissel('WO_45_M_Die', 'WO_53_M_Ola', 'Voor')

start = time.time()
start_oplossing.wens1_berekening()
start_oplossing.wens2_berekening()
start_oplossing.wens3_berekening()
start_oplossing.wens4_berekening()
eind = time.time()

print(eind-start)

y=1