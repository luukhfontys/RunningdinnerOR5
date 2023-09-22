import numpy as np
import matplotlib.pyplot as plt
import math as m
import pandas as pd
from Classes import Deelnemer, Huis
from Functions import ingest_deelnemers, ingest_huizen

deelnemers = ingest_deelnemers('Running Dinner dataset 2022.xlsx')

huizen = ingest_huizen('Running Dinner dataset 2022.xlsx')


x=1