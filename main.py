import numpy as np
import matplotlib.pyplot as plt
import math as m
import pandas as pd
from Classes import Deelnemer, Huis
from Functions import ingest_deelnemers, ingest_huizen, ingest_startoplossing, check_feasible

file_path = 'Running Dinner dataset 2022.xlsx'
startoplossing_path = 'Running Dinner eerste oplossing 2022.xlsx'

#deelnemers in dictionary zetten
deelnemers = ingest_deelnemers(file_path)
#Huizen in dictionary zetten
huizen = ingest_huizen(file_path)

#start oplossing invoeren bij deelnemers en huizen
start_oplossing = ingest_startoplossing(deelnemers, huizen, startoplossing_path)

# start_oplossing.update_aantalgasten()

#Check of start oplossing feasible is.
# start_feasible = check_feasible(deelnemers, huizen)
start_oplossing.gang_kook_wissel('WO79', 'VW35')

start_oplossing.gang_eet_wissel('WO_59_V_Els', 'WO_32_V_Ing', 'Hoofd')

y=1