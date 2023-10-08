import time
from Functions import main_optimizer, ingest_startoplossing, bereken_doelfunctie, export_oplossing, export_performance_rapport

def main():
    #Om de totale rekentijd te kunnen bepalen aan het eind van de code.
    start_tijd = time.time()
    
    #Vul de time out tijd in (hoe lang de optimizer mag blijven hangen op de optimizers.)
    timeout_tijd = 100 #seconden
    
    #Vul de maximale tijd in dat je de optimizer wil laten lopen.
    maximale_rekentijd = 30 # seconden
    
    dataset_file_path = 'Running Dinner dataset 2023 v2.xlsx'
    dataset_file_path_vorigjaar = 'Running Dinner dataset 2022.xlsx' # Als er geen dataset van vorig jaar is zet deze waarde naar None
    startoplossing_path = 'Planning geoptimaliseerd, -1020 0.2m.xlsx'

    #start oplossing inladen
    start_oplossing = ingest_startoplossing(dataset_file_path, dataset_file_path_vorigjaar, startoplossing_path)
    if start_oplossing.feasible() is not True:
        print(f'Start oplossing is niet feasible, probeer een andere start oplossing')
        Score = bereken_doelfunctie(start_oplossing)
        rekenminuten = 0
        export_performance_rapport(start_oplossing, Score, rekenminuten)
        return
    
    #Optimalisatie algoritme 2-opt met random selectie bestaande uit 2 losse optimizers
    optimized_oplossing = main_optimizer(start_oplossing, timeout_tijd, maximale_rekentijd)
    
    #Bereken totale rekentijd:
    eindtijd = time.time()
    rekenminuten = (eindtijd - start_tijd) / 60
    
    #Exporteer oplossing naar excel en print de uiteindelijke score in de terminal
    Score = bereken_doelfunctie(optimized_oplossing)
    export_oplossing(optimized_oplossing, Score, rekenminuten)
    export_performance_rapport(optimized_oplossing, Score, rekenminuten)

if __name__ == '__main__':
    main()