import time
import matplotlib.pyplot as plt
from Functions import main_optimizer, ingest_startoplossing, bereken_doelfunctie, export_oplossing, export_performance_rapport

def main():
    #Om de totale rekentijd te kunnen bepalen aan het eind van de code.
    start_tijd = time.time()
    
    #Vul de time out tijd in (hoe lang de optimizer mag blijven hangen op de optimizers.)
    timeout_tijd = 600000 #seconden
    
    #Vul de maximale tijd in dat je de optimizer wil laten lopen.
    maximale_rekentijd = 10000000 # seconden
    
    dataset_file_path = 'Running Dinner dataset 2023 v2.xlsx'
    dataset_file_path_vorigjaar = 'Running Dinner dataset 2022.xlsx' # Als er geen dataset van vorig jaar is zet deze waarde naar None
    startoplossing_path = 'Running Dinner eerste oplossing 2023 v2.xlsx'

    #start oplossing inladen
    start_oplossing = ingest_startoplossing(dataset_file_path, dataset_file_path_vorigjaar, startoplossing_path)
    
    #Controleren of het feasible is
    if start_oplossing.feasible() is not True:
        Score = bereken_doelfunctie(start_oplossing)
        rekenminuten = 0
        print(f'Start oplossing is niet feasible, probeer een andere start oplossing.\nGenerating performance rapport: Performance rapport, {Score[0]} {round(rekenminuten, 1)}m.xlsx ...')
        export_performance_rapport(start_oplossing, Score, rekenminuten)
        return
    
    #Optimalisatie algoritme 2-opt met random selectie bestaande uit 2 losse optimizers
    optimized_oplossing, test_data = main_optimizer(start_oplossing, timeout_tijd, maximale_rekentijd)
    
    eindtijd = time.time()
    rekenminuten = (eindtijd - start_tijd) / 60
    
    ###Testing
    # tijd = [round(tijd - test_data['Tijd'][0], 2) for tijd in test_data['Tijd']]
    # doelscores = test_data['Doelscore']
    # plt.plot(tijd, doelscores)
    # plt.xlabel('Tijd (s)')
    # plt.ylabel('Gewogen doelscore')
    # plt.title(f'Test plot, totale rekenminuten: {round(rekenminuten, 1)}')
    # plt.show()
    ###
    #Bereken totale rekentijd:

    #Exporteer oplossing naar excel en print de uiteindelijke score in de terminal
    Score = bereken_doelfunctie(optimized_oplossing)
    export_oplossing(optimized_oplossing, Score, rekenminuten)
    export_performance_rapport(optimized_oplossing, Score, rekenminuten)
    
if __name__ == '__main__':
    for i in range(20):
        main() 