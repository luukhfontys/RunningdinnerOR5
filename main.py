import numpy as np
import matplotlib.pyplot as plt
import math as m
import pandas as pd

class Deelnemer:
    def __init__(self, naam: str, adres: str, kookt, ):
        self.naam = naam
        self.adres = adres
        self.kookt = kookt


df = pd.read_excel('Running Dinner dataset 2022.xlsx')

deelnemers = []

for index, row in df.iterrows():
    naam = row['Bewoner']
    adres = row['Huisadres']
    kookt = row['Kookt niet']
    deelnemer = Deelnemer(naam, adres, kookt)
    deelnemers.append(deelnemer)

print(deelnemers[1].kookt)

