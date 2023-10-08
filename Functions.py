import pandas as pd
import copy
import time
import random
import logging
from logger_utils import logger
from Classes import Deelnemer, Huis, Oplossing

logger = logging.getLogger(name='2opt-logger')

def main_optimizer(huidige_oplossing, timeout_tijd, maximale_rekentijd) -> object:
    
    start_tijd = time.time()
    rekentijd = 0
    
    deelnemer_namen = [deelnemer for deelnemer in huidige_oplossing.deelnemers]
    #Hier worden huizen die vrijstelling hebben meteen eruit gefiltert
    huis_adressen = [huis for huis in huidige_oplossing.huizen if not huidige_oplossing.huizen[huis].kook_vrijstelling]
    gangen = ['Voor', 'Hoofd', 'Na']
    
    test_data = {'Tijd': [],
                 'Doelscore': []}
    
    unieke_deelnemer_combinaties = generate_uniek(deelnemer_namen)
    unieke_huis_combinaties = generate_uniek(huis_adressen)
    
    stuck = False
    while (stuck == False) and (rekentijd < maximale_rekentijd):
        keuzegetal = random.choice(['eet_gang', 'kook_gang'])
        
        huidige_tijd = time.time()
        rekentijd = huidige_tijd - start_tijd
        
        if keuzegetal == 'eet_gang':
            huidige_oplossing, improvedeet = eet_gang_optimizer(huidige_oplossing, unieke_deelnemer_combinaties, gangen, timeout_tijd)
            if improvedeet == False:
                logger.debug(msg=f"*eet_gang_optimizer* Timeout: {timeout_tijd}s trying kook_gang_optimizer")
                print(f"*eet_gang_optimizer* Timeout: {timeout_tijd}s trying kook_gang_optimizer")
                huidige_oplossing, improvedkook = kook_gang_optimizer(huidige_oplossing, unieke_huis_combinaties, timeout_tijd)
                if improvedkook == False:
                    logger.debug(msg=f"*kook_gang_optimizer* Timeout: {timeout_tijd}s Optimizer stopping ...")
                    print(f"*kook_gang_optimizer* Timeout: {timeout_tijd}s Optimizer stopping ...")
                    stuck = True
        
        if keuzegetal == 'kook_gang':
            huidige_oplossing, improvedkook = kook_gang_optimizer(huidige_oplossing, unieke_huis_combinaties, timeout_tijd)
            if improvedkook == False:
                logger.debug(msg=f"*kook_gang_optimizer* Timeout: {timeout_tijd}s trying eet_gang_optimizer")
                print(f"*kook_gang_optimizer* Timeout: {timeout_tijd}s trying eet_gang_optimizer")
                huidige_oplossing, improvedeet = eet_gang_optimizer(huidige_oplossing, unieke_deelnemer_combinaties, gangen, timeout_tijd)
                if improvedeet == False:
                    logger.debug(msg=f"*eet_gang_optimize* Timeout: {timeout_tijd}s Optimizer stopping ...")
                    print(f"*eet_gang_optimize* Timeout: {timeout_tijd}s Optimizer stopping ...")
                    stuck = True
                    
        ####Data voor latere analyse opslaan ###Testing
        test_data['Tijd'].append(time.time())
        test_data['Doelscore'].append(bereken_doelfunctie(huidige_oplossing)[0])
        ###
    return huidige_oplossing, test_data

def ingest_deelnemers(file_path: str) -> dict:
    """Deze functie neemt een excel file path, stopt de bijbehorende excel file vervolgens in een DataFrame 
    en daarna wordt alle deelnemer informatie in een dictionary van objecten geplaatst.
    
    Parameters:
        file_path (str): Bestand locatie van de dataset excel file
        
    Returns:
        dict: Een dictionary met de deze layout:
    
    Voorbeeld:
        >>> ingest_deelnemers('Running dinner dataset 2023.xlsx')
        {'Naam van deelnemer 1': Deelnemer object met alle statische data van deelnemer 1,
        'Naam van deelnemer 2': Deelnemer object met alle statische data van deelnemer 2, ... }
    """
    ## Deelnemer input waardes

    #Alle deelnemers in een dataframe zetten
    df_deelnemers = pd.read_excel(file_path, sheet_name = 'Bewoners')

    #Dictionary initializen
    deelnemers = dict()

    # Voeg alles namen en adressen van deelnemers toe in dictionary van classes
    for index, row in df_deelnemers.iterrows():
        naam = row['Bewoner']
        adres = row['Huisadres']
        deelnemer = Deelnemer(naam, adres)
        deelnemers[deelnemer.naam] = deelnemer

    #Sla op wie er bij elkaar moet blijven
    df_bijelkaar = pd.read_excel(file_path, sheet_name = 'Paar blijft bij elkaar', skiprows=[0])

    for index, row in df_bijelkaar.iterrows():
        #Alle paren verkrijgen uit deelnemers dictionary van objecten
        bewoner1 = deelnemers.get(row["Bewoner1"])
        bewoner2 = deelnemers.get(row["Bewoner2"])
        
        #Alle paren bij elkaar in het object opslaan
        bewoner1.bijelkaarblijven = bewoner2
        bewoner2.bijelkaarblijven = bewoner1

    #Alle directe buren opslaan per deelnemer
    df_directe_buren = pd.read_excel(file_path, sheet_name = 'Buren', skiprows=[0])
    
    #Loop over alle rijen van dataframe
    for i in range(len(df_directe_buren)):
        
        #Neem linker kolom als deelnemer object, de rechter kolom als persoon die toegevoegd wordt aan de buren van het deelnemer object
        deelnemers[df_directe_buren.iloc[i, 0]].buren.append(deelnemers[df_directe_buren.iloc[i, 1]].naam)
    
    #Alle tafelgenoten van vorigjaar inladen
    df_tafelgenoten_vorigjaar = pd.read_excel(file_path, sheet_name = 'Tafelgenoot vorig jaar', skiprows=[0])
    for i in range(len(df_tafelgenoten_vorigjaar)):
        
        #Selecteer bewoner waar tafelgenoten voor geregistreerd gaan worden
        huidige_bewoner = df_tafelgenoten_vorigjaar['Bewoner1'][i]
        
        #Controleren of huidige bewoner dit jaar ook nog mee doet.
        if deelnemers.get(huidige_bewoner) is not None:
            
            #Zo ja, voeg de tafel genoot van kolom 2 toe aan de self.tafelgenootvorigjaar attribute.
            deelnemers[huidige_bewoner].tafelgenootvorigjaar.append(df_tafelgenoten_vorigjaar['Bewoner2'][i])

    return deelnemers

def ingest_tafelgenoten_2_jaar_geleden(file_path: str, deelnemers: dict) -> dict:
    df_tafel_genoten_2_jaar_geleden = pd.read_excel(file_path, sheet_name = 'Tafelgenoot vorig jaar', skiprows=[0])
    for i in range(len(df_tafel_genoten_2_jaar_geleden)):
        huidige_bewoner = df_tafel_genoten_2_jaar_geleden['Bewoner1'][i]
        if deelnemers.get(huidige_bewoner) is not None:
            deelnemers[huidige_bewoner].tafelgenoten2jaargeleden.append(df_tafel_genoten_2_jaar_geleden['Bewoner2'][i])
    return deelnemers

def ingest_huizen(file_path: str) -> dict:
    """Deze functie neemt een excel file path, stopt de bijbehorende excel file vervolgens in een DataFrame 
    en daarna wordt alle huis informatie in een dictionary van objecten geplaatst.
    
    Parameters:
        file_path (str): Bestand locatie van de dataset excel file
        
    Returns:
        dict: Een dictionary met de deze layout:
    
    Voorbeeld:
        >>> ingest_huizen('Running dinner dataset 2023.xlsx')
        {'Huis adres 1': Huis object met alle statische data van huis adres 1,
        'Huis adres 2': Huis object met alle statische data van huis adres 2, ... }
    """
    
    #Input waardes voor huizen en deelnemers
    df_huizen = pd.read_excel(file_path, sheet_name = 'Adressen')
    df_deelnemers = pd.read_excel(file_path, sheet_name = 'Bewoners')
    df_kookte_vorig_jaar = pd.read_excel(file_path, sheet_name = 'Kookte vorig jaar', skiprows=[0])

    #Initialiseer dictionary voor objecten in op te slaan
    huizen = dict()

    #Loop voor elk huis in df_huizen
    for index, row in df_huizen.iterrows():
        adres = row['Huisadres']
        min_gasten = row['Min groepsgrootte']
        max_gasten = row['Max groepsgrootte']
        gang_voorkeur = row['Voorkeur gang']
        
        #als er geen min of max aangegeven is vervang nan met 0
        if pd.isna(min_gasten):
            min_gasten = 0
            max_gasten = 0
        
        #Maak huis object met alles behalve gang voorkeur
        huis = Huis(adres, min_gasten, max_gasten)
        
        #Check of huis een gang voorkeur heeft
        if not pd.isna(gang_voorkeur):
            
            #Zo ja, voeg het toe aan het huis object
            huis.gang_voorkeur = gang_voorkeur
        
        #Sla het huis op in huizen dictionary, met het huis adres als key.
        huizen[huis.adres] = huis
    
    #bijhouden welke bewoners waar wonen en of ze vrijstelling van koken hebben of niet
    for index, row in df_deelnemers.iterrows():
        
        #Deelnemer bij zijn/haar woning toevoegen als bewoner
        huizen[row['Huisadres']].bewoners.append(row['Bewoner'])
        
        #Controleren of dit persoon niet kookt
        if row['Kookt niet'] == 1:
            
            #Kook vrijstelling registreren als persoon niet kookt.
            huizen[row['Huisadres']].kook_vrijstelling = True
    
    #alle gekookte gangen vorig jaar registreren bij behorende huisadres
    for index, row in df_kookte_vorig_jaar.iterrows():
        
        #Rekening houden met huizen die mogelijk vorig jaar niet mee deden, dus ook geen gang vorig jaar gekookt hebben.
        if huizen.get(row['Huisadres']) is not None:
            
            #Vorig jaar gekookte gang registreren bij huis adres.
            huizen[row['Huisadres']].kookte_vorigjaar = row['Gang']
    
    return huizen

def ingest_startoplossing(dataset_file_path: str, dataset_file_path_vorigjaar: str, startoplossing_path: str) -> object:
    """Deze functie neemt een start oplossing excel file path en stopt de bijbehorende excel file vervolgens in een DataFrame.
    deze informatie wordt in opgeslagen in een oplossing object samen met alle statische informatie van deelnemers en huizen dictionaries.
    
    Parameters:
        dataset_file_path (str): string met de locatie van de dataset file
        dataset_file_path_vorigjaar (str): string met de locatie van de dataset file van vorig jaar
        startoplossing_path (str): Bestand locatie van de start oplossing excel file
        
    Returns:
        object: Oplossing object met een start planning en alle informatie over de deelnemers en huizen.
    """
    
    #deelnemers in dictionary zetten
    deelnemers = ingest_deelnemers(dataset_file_path)
    #Data 2 jaar geleden laden indien deze is gegeven
    if dataset_file_path_vorigjaar is not None:
        deelnemers = ingest_tafelgenoten_2_jaar_geleden(dataset_file_path_vorigjaar, deelnemers)
    #Huizen in dictionary zetten
    huizen = ingest_huizen(dataset_file_path)
    
    #Start oplossing in dataframe zetten
    df_startoplossing = pd.read_excel(startoplossing_path)

    #voor hoofd, nagerecht bij deelnemers in de class zetten.
    oplossing = Oplossing(deelnemers, huizen)
    
    #Loop over start planning voor alle deelnemers
    for i in range(len(df_startoplossing)):
        
        #Registreer alle gangen en een start aantal gasten van 0, (Dit wordt met de Oplossing.update_aantalgasten attribute later vanzelf berekent)
        oplossing.oplossing[
            df_startoplossing['Bewoner'][i]] = [df_startoplossing['kookt'][i],
                                                df_startoplossing['Voor'][i],
                                                df_startoplossing['Hoofd'][i],
                                                df_startoplossing['Na'][i],
                                                0]

    return oplossing

def bereken_doelfunctie(oplossing: object) -> (int, bool):
    oplossing.Bereken_alle_wensen()
    feasible = oplossing.feasible()
    Score = oplossing.doelfunctie
    return Score, feasible

def generate_uniek(lijst: list) -> list:
    """
    Genereer een lijst met unieke combinaties van elementen uit de gegeven lijst.
    Neem n als lengte van de inputlijst.
    De Functie genereerd n! / (2! * (n - 2)!) combinaties.

    Parameters:
        lijst (list): De invoerlijst waaruit unieke combinaties worden gegenereerd.

    Returns:
        list: Lijst van tuples die unieke combinaties van elementen uit de invoerlijst bevatten.

    Voorbeeld:
        >>> generate_uniek([1, 2, 3])
        [(1, 2), (1, 3), (2, 3)]
    """
    
    unieke_combinaties = []
    
    #Loop over de elementen van de lijst om combinaties te genereren.
    for i in range(len(lijst)):
        for j in range(i+1, len(lijst)):
            
            #Voeg de combinatie toe aan de lijst.
            unieke_combinaties.append((lijst[i], lijst[j]))
            
    return unieke_combinaties

def eet_swap(oplossing: object, deelnemer1: str, deelnemer2: str, gang: str):
    """
    Maakt een kopie van de huidige oplossing en wisselt de gegeven eet gang van 2 deelnemers.
    
    Parameters:
        oplossing (object): Het oorspronkelijke oplossingsobject waarop de bewerking wordt toegepast.
        deelnemer1 (str): De naam van de eerste deelnemer die wordt gewisseld.
        deelnemer2 (str): De naam van de tweede deelnemer die wordt gewisseld.
        gang (str): De specifieke gang waarin de deelnemers worden gewisseld.
    
    Returns:
        object: Een kopie van het gewijzigde oplossingsobject met deelnemers 'deelnemer1' en 'deelnemer2' gewisseld
                voor de opgegeven eet gang.
    """
    
    #Maak kopie van huidige oplossing
    nieuwe_oplossing = copy.deepcopy(oplossing)
    
    #Wissel eet gang met gegeven gang op kopie
    nieuwe_oplossing.gang_eet_wissel(deelnemer1, deelnemer2, gang)
    
    #zorg dat mensen die bij elkaar moeten blijven ook bij elkaar blijven.
    nieuwe_oplossing.sync_attributen
    
    return nieuwe_oplossing

def kook_swap(oplossing: object, adres1: str, adres2: str):
    """
    Maakt een kopie van de huidige oplossing en wisselt de gegeven kook gang van 2 adressen.
    
    Parameters:
        oplossing (object): Het oorspronkelijke oplossingsobject waarop de bewerking wordt toegepast.
        adres1 (str): Het eerste adres die wordt gewisseld.
        adres2 (str): Het tweede adres die wordt gewisseld.
    
    Returns:
        object: Een kopie van het oplossingsobject met adressen 'adres1' en 'adres2' gewisseld
                voor de opgegeven kook gang.
    """
    
    #Maak kopie van huidige oplossing
    nieuwe_oplossing = copy.deepcopy(oplossing)
    
    #Wissel kook gang voor adressen 1 en 2
    nieuwe_oplossing.gang_kook_wissel(adres1, adres2)
    
    #zorg dat mensen die bij elkaar moeten blijven ook bij elkaar blijven.
    nieuwe_oplossing.sync_attributen
    
    return nieuwe_oplossing

def export_oplossing(oplossing, Score, rekentijd_minuten):
    """
    Exporteer de oplossing naar een Excel-bestand.

    Parameters:
        oplossing: De oplossing die moet worden geëxporteerd.
        Score: De score van de oplossing.
        rekentijd_minuten: De tijd die nodig was om de oplossing te berekenen in minuten.

    Opmerkingen:
        Deze functie maakt een DataFrame van de oplossing en voegt extra kolommen toe voor 'Huisadres'.
        Vervolgens wordt het DataFrame geëxporteerd naar een Excel-bestand met een naam op basis van de score
        en de berekende rekentijd.
    """
    
    #Maak een DataFrame van de oplossing
    df_oplossing = pd.DataFrame.from_dict(oplossing.oplossing, orient='index')
    df_oplossing = df_oplossing.reset_index()
    df_oplossing.columns = ['Bewoner' , 'kookt', 'Voor', 'Hoofd', 'Na', 'aantal']
    
    #Wijzig de kolomvolgorde om 'kookt' op de tweede positie te plaatsen
    df_oplossing.insert(4, 'kookt', df_oplossing.pop('kookt'))
    
    # Voeg een kolom 'Huisadres' toe op basis van de adresgegevens van de bewoners
    df_oplossing.insert(1, 'Huisadres', '')
    for i in range(len(df_oplossing['Bewoner'])):
        bewoner = df_oplossing['Bewoner'][i]
        adres = oplossing.deelnemers[bewoner].adres
        df_oplossing.at[i, 'Huisadres'] = adres
    
    # Exporteer het DataFrame naar een Excel-bestand met een naam op basis van de score en rekentijd
    df_oplossing.to_excel(f'Planning geoptimaliseerd, {Score[0]} {round(rekentijd_minuten, 1)}m.xlsx', index=True)
    
    #In de terminal de uiteindelijke score printen
    print(Score)
    
def export_performance_rapport(oplossing: object, Score, rekentijd_minuten):
    
    #Alle waardes pakken, in geval van score 3, kijken hoeveel er niet een voorkeursgang kregen
    performance_waardes = [oplossing.Score_wens1, oplossing.Score_wens2, oplossing.totaal_aantal_voorkeuren_huishouden() - oplossing.Score_wens3, 
                           oplossing.Score_wens4, oplossing.Score_wens5, oplossing.Score_wens6]
    performance_waardes = [abs(waarde) for waarde in performance_waardes]
    
    Eis_waardes = [oplossing.aantal_personen_niet_ingedeeld, oplossing.aantal_personen_dat_niet_kookt_maar_wel_moet,
                   oplossing.kookt_niet_op_eigen_adres, oplossing.not_in_capacity[0], oplossing.aantal_personen_dat_bijelkaar_moet_blijven_maar_dit_niet_zijn, None]
    
    Eis_descriptors = ['Aantal personen dat niet is ingedeeld op één of meer gangen', 'Aantal personen dat zonder vrijstelling toch niet kookt',
                       'Aantal personen dat niet op eigen adres staat ingedeeld voor de gang die deze deelnemer moet koken',
                       'Aantal keren dat het minimum of maximum aantal gasten wordt geschonden (mensen met vrijstelling hebben min en max van 0)',
                       'Aantal keren dat duos die bij elkaar moeten blijven niet bij elkaar blijven', None]
    
    Descriptors = ['Aantal personen dat vaker dan 1 keer bij elkaar aan tafel zitten:', 'Aantal huishoudens dat wederom een hoofdgerecht moet bereiden', 'Aantal huishoudens dat niet het voorkeursgerecht krijgt toegewezen', 'Aantal keer dat deelnemers wederom als voorgaand jaar samen eten', 'Aantal keer dat buren samen eten', 'Aantal keer dat deelnemers wederom als 2 jaar geleden samen eten']
    
    data = {'Wens': Descriptors,
            'Wens data': performance_waardes,
            'Eis': Eis_descriptors,
            'Eis data': Eis_waardes}
    
    df_performance_rapport = pd.DataFrame(data)
    df_performance_rapport.to_excel(f'Performance rapport, {Score[0]} {round(rekentijd_minuten, 1)}m.xlsx')
    
def eet_gang_optimizer(oplossing: object, unieke_deelnemer_combinaties: list, gangen: list, timeout_tijd: int) -> (object, bool):
    """
    Optimaliseerd oplossing door willekeurig eet gangen te wisselen en kijken of de doel score verbeterd of niet.
    
    Parameters:
        oplossing (object): De initial oplossing die moet worden geoptimaliseerd.
        unieke_deelnemer_combinaties (list): Een lijst met unieke combinaties van deelnemers gegenereerd door generate_uniek().
        gangen (list): Een lijst met gangen.
        timeout_tijd (int): Timeout na deze duur (in seconden).
    
    Returns:
        tuple: Een tuple bestaande uit de geoptimaliseerde oplossing en een boolean die aangeeft of de oplossing is verbeterd.
    """
    
    #Shuffle combinaties voor random volgorde van 2-opt
    random.shuffle(unieke_deelnemer_combinaties)
    
    #Initialiseer waardes
    improved = False
    i = 0
    j = 0
    start_tijd = time.time()
    rekentijd = 0
    
    #Terwijl de oplossing niet verbeterd, we niet door alle combinaties heen zijn 
    #en de rekentijd niet over de timeout tijd is gegaan, blijf loopen.
    while not improved and (i < len(unieke_deelnemer_combinaties)) and (rekentijd < timeout_tijd):
        
        #Voor elke unieke deelnemer combinatie check elke gang.
        for gang in gangen:
            
            #Wissel eetgang voor unieke deelnemer combinatie i.
            nieuwe_oplossing = eet_swap(oplossing, unieke_deelnemer_combinaties[i][0], unieke_deelnemer_combinaties[i][1], gang)
            
            #Bereken doelfunctie en feasibility voor nieuwe oplossing
            scorenieuw, feasible = bereken_doelfunctie(nieuwe_oplossing)
            
            #Bereken doelfunctie van huidige oplossing (voor de huidige oplossing nemen we aan dat die feasible is)
            scorehuidig, _ = bereken_doelfunctie(oplossing)
            
            #Check of nieuwe oplossing beter is en feasible
            if (scorenieuw > scorehuidig) and feasible:
                
                #Nieuwe vondst in een debug .log zetten en printen in de terminal
                logger.debug(msg=f"*eet_gang_optimizer* Bij iteratie: {j}, Nieuwe oplossing score van: {scorenieuw} > {scorehuidig}, {unieke_deelnemer_combinaties[i][0]} en {unieke_deelnemer_combinaties[i][1]} zijn hiervoor gewisseld.")
                print(f"*eet_gang_optimizer* Bij iteratie: {j}, Nieuwe oplossing score van: {scorenieuw} > {scorehuidig}, {unieke_deelnemer_combinaties[i][0]} en {unieke_deelnemer_combinaties[i][1]} zijn hiervoor gewisseld.")
                
                #improved naar waar zetten en vervolgens nieuwe oplossing en improved returnen.
                improved = True
                return nieuwe_oplossing, improved
        
            #Kijken hoe lang we al aan het rekenen zijn voor huidige optimalisatie poging
            huidige_tijd = time.time()
            rekentijd = huidige_tijd - start_tijd
            
            j += 1
            #Voor elke 10 gangen, print de rekentijd van de huidige optimalisatie poging, de iteratie en de optimizer die gebruikt wordt in de terminal
            if j %10 == 0:
                print(f'rekentijd: {round(rekentijd, 1)}s, iteratie: {i}, optimizer: eet gang', end='\r')
        
        #Als oplossing niet verbeterd iteration +1
        i += 1
    #Als er geen optimalisatie binnen de time out tijd kon worden gevonden, return oplossing en improved = False
    return oplossing, improved

def kook_gang_optimizer(oplossing: object, unieke_huis_combinaties: list, timeout_tijd: int) -> (object, bool):
    """
    Optimaliseerd oplossing door willekeurig kook gangen te wisselen en kijken of de doel score verbeterd of niet.
    
    Parameters:
        oplossing (object): De initial oplossing die moet worden geoptimaliseerd.
        unieke_huis_combinaties (list): Een lijst met unieke combinaties van huizen gegenereerd door generate_uniek().
        gangen (list): Een lijst met gangen.
        timeout_tijd (int): Timeout na deze duur (in seconden).
    
    Returns:
        tuple: Een tuple bestaande uit de geoptimaliseerde oplossing en een boolean die aangeeft of de oplossing is verbeterd.
    """
    
    #Shuffle combinaties voor random volgorde van 2-opt
    random.shuffle(unieke_huis_combinaties)
    
    #Initialiseer waardes
    improved = False
    i = 0
    start_tijd = time.time()
    rekentijd = 0
    
    #Terwijl de oplossing niet verbeterd, we niet door alle combinaties heen zijn 
    #en de rekentijd niet over de timeout tijd is gegaan, blijf loopen.
    while not improved and (i < len(unieke_huis_combinaties)) and (rekentijd < timeout_tijd):
        
        #Wissel kookgang voor unieke huis combinatie i.
        nieuwe_oplossing = kook_swap(oplossing, unieke_huis_combinaties[i][0], unieke_huis_combinaties[i][1])
        
        #Bereken doelfunctie en feasibility voor nieuwe oplossing
        scorenieuw, feasible = bereken_doelfunctie(nieuwe_oplossing)
        
        #Bereken doelfunctie van huidige oplossing (voor de huidige oplossing nemen we aan dat die feasible is)
        scorehuidig, _ = bereken_doelfunctie(oplossing)
        
        #Check of nieuwe oplossing beter is en feasible
        if (scorenieuw > scorehuidig) and feasible:
            
            #Nieuwe vondst in een debug .log zetten en printen in de terminal
            logger.debug(msg=f"*kook_gang_optimizer* Bij iteratie: {i}, Nieuwe oplossing score van: {scorenieuw} > {scorehuidig}, {unieke_huis_combinaties[i][0]} en {unieke_huis_combinaties[i][1]} zijn hiervoor gewisseld.")
            print(f"*kook_gang_optimizer* Bij iteratie: {i}, Nieuwe oplossing score van: {scorenieuw} > {scorehuidig}, {unieke_huis_combinaties[i][0]} en {unieke_huis_combinaties[i][1]} zijn hiervoor gewisseld.")
            
            #improved naar waar zetten en vervolgens nieuwe oplossing en improved returnen.
            improved = True
            return nieuwe_oplossing, improved
        
        #Als oplossing niet verbeterd iteration +1
        i += 1
        
        #Kijken hoe lang we al aan het rekenen zijn voor huidige optimalisatie poging
        huidige_tijd = time.time()
        rekentijd = huidige_tijd - start_tijd
        
        #Voor elke 10 iteraties, print de rekentijd van de huidige optimalisatie poging, de iteratie en de optimizer de gebruikt wordt in de terminal
        if i %10 == 0:
            print(f'rekentijd: {round(rekentijd, 1)}s, iteratie: {i}, optimizer: kook gang', end='\r')

    #Als er geen optimalisatie binnen de time out tijd kon worden gevonden, return oplossing en improved = False
    return oplossing, improved