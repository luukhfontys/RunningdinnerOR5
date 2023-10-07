import time
import random
from logger_utils import logger
from Functions import ingest_deelnemers, ingest_huizen, ingest_startoplossing, ingest_tafelgenoten_2_jaar_geleden, bereken_doelfunctie, generate_uniek, export_oplossing, kook_gang_optimizer, eet_gang_optimizer

def main():
    timeout_tijd = 10000 #seconden
    start_tijd = time.time()
    file_path = 'Running Dinner dataset 2023 v2.xlsx'
    file_path_vorigjaar = 'Running Dinner dataset 2022.xlsx'
    startoplossing_path = 'Planning geoptimaliseerd, -258 28.3m.xlsx'

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
        
    eindtijd = time.time()
    rekenminuten = (eindtijd - start_tijd) / 60
    Score = bereken_doelfunctie(huidige_oplossing)
    export_oplossing(huidige_oplossing, Score, rekenminuten)
    print(Score)

if __name__ == '__main__':
    main()