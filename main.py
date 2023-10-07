import time
from Functions import main_optimizer, ingest_deelnemers, ingest_huizen, ingest_startoplossing, ingest_tafelgenoten_2_jaar_geleden, bereken_doelfunctie, generate_uniek, export_oplossing, kook_gang_optimizer, eet_gang_optimizer

def main():
    timeout_tijd = 20 #seconden
    start_tijd = time.time()
    file_path = 'Running Dinner dataset 2023 v2.xlsx'
    file_path_vorigjaar = 'Running Dinner dataset 2022.xlsx'
    startoplossing_path = 'Running Dinner eerste oplossing 2023 v2.xlsx'

    #deelnemers in dictionary zetten
    deelnemers = ingest_deelnemers(file_path)
    #Data 2 jaar geleden laden indien deze is gegeven
    if file_path_vorigjaar is not None:
        deelnemers = ingest_tafelgenoten_2_jaar_geleden(file_path_vorigjaar, deelnemers)
    #Huizen in dictionary zetten
    huizen = ingest_huizen(file_path)

    #start oplossing invoeren bij deelnemers en huizen
    start_oplossing = ingest_startoplossing(deelnemers, huizen, startoplossing_path)
    
    #Optimalisatie algoritme 2-opt
    optimized_oplossing = main_optimizer(start_oplossing, timeout_tijd)
    
    #Bereken totale rekentijd:
    eindtijd = time.time()
    rekenminuten = (eindtijd - start_tijd) / 60
    
    #Exporteer oplossing naar excel en print de uiteindelijke score in de terminal
    Score = bereken_doelfunctie(optimized_oplossing)
    export_oplossing(optimized_oplossing, Score, rekenminuten)
    print(Score)

if __name__ == '__main__':
    main()