import numpy as np

def objective(x: np.ndarray) -> float:
    return 20 * x[0] - 4 * x[1] + 14 * x[2]

def check_feasible(x: np.ndarray) -> bool:
    constraint1 = 2 * x[0] + x[1] + 4 * x[2] <= 5
    constraint2 = all(val in [0, 1] for val in x)
    return constraint1 and constraint2

def check_improving(x: np.ndarray, xminus: np.ndarray) -> bool:
    return objective(x) > objective(xminus)

moveset = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1], [-1, 0, 0], [0, -1, 0], [0, 0, -1]])

startsol = np.array([1, 1, 0])
t = 0
locally_optimal = False
currentsol = startsol

while not locally_optimal:
    neighbourhood = []
    
    for move in range(len(moveset)):
        neighbourhood.append(currentsol + moveset[move])
    neighbourhood = np.array(neighbourhood)
    
    feasible = 0
    improving = 0
    for neighbour in neighbourhood:
        if check_feasible(neighbour):
            feasible += 1
            if check_improving(neighbour, currentsol):
                improving += 1
                currentsol = neighbour
    if improving == 0:
        locally_optimal = True



print(f'solution: {currentsol} objective: {objective(currentsol)}')