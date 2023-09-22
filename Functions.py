import pandas as pd
from Classes import Deelnemer, Huis

def ingest_huizen(file_path: str) -> dict:
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