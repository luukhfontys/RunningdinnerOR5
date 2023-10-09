import time
import tkinter as tk

from tkinter import filedialog
import threading
# import matplotlib.pyplot as plt
from Functions import main_optimizer, ingest_startoplossing, bereken_doelfunctie, export_oplossing, export_performance_rapport

class InputWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Running dinner optimizer 2023 Luuk Hooymans")
        
        self.geometry("500x300")
        
        self.timeout_label = tk.Label(self, text="Timeout Tijd (s):")
        self.timeout_entry = tk.Entry(self)
        
        self.max_time_label = tk.Label(self, text="Maximale Rekentijd (s):")
        self.max_time_entry = tk.Entry(self)
        
        self.dataset_label = tk.Label(self, text="Dataset File Path:")
        self.dataset_entry = tk.Entry(self)
        self.dataset_button = tk.Button(self, text="Browse", command=self.browse_dataset)
        
        self.dataset_vorigjaar_label = tk.Label(self, text="Dataset File Path (Vorigjaar):")
        self.dataset_vorigjaar_entry = tk.Entry(self)
        self.dataset_vorigjaar_button = tk.Button(self, text="Browse", command=self.browse_dataset_vorigjaar)
        
        self.startoplossing_label = tk.Label(self, text="Startoplossing File Path:")
        self.startoplossion_entry = tk.Entry(self)
        self.startoplossion_button = tk.Button(self, text="Browse", command=self.browse_startoplossion)
        
        self.h_label = tk.Label(self, text="Herhalingen:")
        self.h_entry = tk.Entry(self)
        
        self.calculate_button = tk.Button(self, text="Start Calculating", command=self.start_calculating)
        
        self.timeout_label.grid(row=0, column=0, padx=10, pady=5, sticky="e")
        self.timeout_entry.grid(row=0, column=1, padx=10, pady=5)
        
        self.max_time_label.grid(row=1, column=0, padx=10, pady=5, sticky="e")
        self.max_time_entry.grid(row=1, column=1, padx=10, pady=5)
        
        self.dataset_label.grid(row=2, column=0, padx=10, pady=5, sticky="e")
        self.dataset_entry.grid(row=2, column=1, padx=10, pady=5)
        self.dataset_button.grid(row=2, column=2, padx=10, pady=5)
        
        self.dataset_vorigjaar_label.grid(row=3, column=0, padx=10, pady=5, sticky="e")
        self.dataset_vorigjaar_entry.grid(row=3, column=1, padx=10, pady=5)
        self.dataset_vorigjaar_button.grid(row=3, column=2, padx=10, pady=5)
        
        self.startoplossing_label.grid(row=4, column=0, padx=10, pady=5, sticky="e")
        self.startoplossion_entry.grid(row=4, column=1, padx=10, pady=5)
        self.startoplossion_button.grid(row=4, column=2, padx=10, pady=5)
        
        self.h_label.grid(row=5, column=0, padx=10, pady=5, sticky="e")
        self.h_entry.grid(row=5, column=1, padx=10, pady=5)
        
        self.calculate_button.grid(row=6, column=0, columnspan=3, padx=10, pady=10)
        
    def browse_dataset(self):
        file_path = filedialog.askopenfilename()
        self.dataset_entry.delete(0, tk.END)
        self.dataset_entry.insert(0, file_path)
    
    def browse_dataset_vorigjaar(self):
        file_path = filedialog.askopenfilename()
        self.dataset_vorigjaar_entry.delete(0, tk.END)
        self.dataset_vorigjaar_entry.insert(0, file_path)
    
    def browse_startoplossion(self):
        file_path = filedialog.askopenfilename()
        self.startoplossion_entry.delete(0, tk.END)
        self.startoplossion_entry.insert(0, file_path)
    
    def start_calculating(self):
        timeout_tijd = int(self.timeout_entry.get())
        maximale_rekentijd = int(self.max_time_entry.get())
        dataset_file_path = str(self.dataset_entry.get())
        dataset_file_path_vorigjaar = str(self.dataset_vorigjaar_entry.get())
        startoplossing_path = str(self.startoplossion_entry.get())
        h = int(self.h_entry.get())
        calculation_thread = threading.Thread(target=self.perform_calculation, args=(timeout_tijd, maximale_rekentijd, dataset_file_path, dataset_file_path_vorigjaar, startoplossing_path, h))
        calculation_thread.start()
        
    def perform_calculation(self, timeout_tijd, maximale_rekentijd, dataset_file_path, dataset_file_path_vorigjaar, startoplossing_path, h):
        for i in range(h):
            #Om de totale rekentijd te kunnen bepalen aan het eind van de code.
            start_tijd = time.time()
            
            #Vul de time out tijd in (hoe lang de optimizer mag blijven hangen op de optimizers.)
            # timeout_tijd = 300 #seconden
            
            # #Vul de maximale tijd in dat je de optimizer wil laten lopen.
            # maximale_rekentijd = 3600/2 # seconden
            
            # dataset_file_path = 'Running Dinner dataset 2023 v2.xlsx'
            # dataset_file_path_vorigjaar = 'Running Dinner dataset 2022.xlsx' # Als er geen dataset van vorig jaar is zet deze waarde naar None
            # startoplossing_path = 'Running Dinner eerste oplossing 2023 v2.xlsx'

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
            
            #Bereken totale rekentijd:
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
        

            #Exporteer oplossing naar excel en print de uiteindelijke score in de terminal
            Score = bereken_doelfunctie(optimized_oplossing)
            export_oplossing(optimized_oplossing, Score, rekenminuten)
            export_performance_rapport(optimized_oplossing, Score, rekenminuten)
        
if __name__ == '__main__':
    app = InputWindow()
    app.mainloop()