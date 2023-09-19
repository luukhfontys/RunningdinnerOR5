# Solving Traveling Salesman Problem by applying Discrete Improving Search (local search)
# Neighborhood structure/Move: 2-exchange
# - remove two arcs, not sharing a node -> three paths
# - reconnect the three paths and form a new dicycle, by inserting two arcs

import random
import logging

logger = logging.getLogger(name='2opt-logger')
logging.basicConfig(level=logging.DEBUG,
                    format='[%(asctime)s] %(message)s',
                    handlers=[logging.FileHandler("2-opt_debug-my.log")])

def euclidean_distance(point1, point2):
    x1, y1 = point1
    x2, y2 = point2
    return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5

def total_distance(tour, points):
    distance = 0
    for i in range(len(tour)):
        distance += euclidean_distance(points[tour[i]], points[tour[(i + 1) % len(tour)]])
    return distance

def two_opt(tour, points):
    improved = True
    while improved:
        improved = False
        total_distance_tour = total_distance(tour, points)
        logger.debug(msg=f"tour has total distance: {total_distance_tour}")
        i = 1
        while ((i <= len(tour)-2) and not(improved)):
            j = i+1
            while((j <= len(tour)) and not(improved)): 
                if j - i == 1:
                    j += 1
                    continue  # No need to reverse two consecutive edges
                new_tour = tour[:]
                new_tour[i:j] = reversed(tour[i:j])
                total_distance_new_tour = total_distance(new_tour, points)
                if total_distance(new_tour, points) < total_distance(tour, points):
                    logger.debug(msg=f"new tour has total distance: {total_distance_new_tour}, so: Improvement for i,j={i},{j}")
                    tour = new_tour
                    logger.debug(msg=f"tour updated: tour={tour}")
                    improved = True
                else:
                    logger.debug(msg=f"new tour has total distance: {total_distance_new_tour}, so:No improvement for i,j={i},{j}")
                j += 1
            i += 1
    return tour

def main():
    # Define a list of points (coordinates) for the TSP
    points = [(0, 0), (1, 2), (2, 4), (3, 1), (4, 3)]

    # Create an initial tour (random permutation of points)
    """"
    tour = list(range(len(points)))
    random.shuffle(tour) 
    """    
    tour = [0, 3, 2, 1, 4]
    logger.debug(msg=f"Initial solution: Tour={tour}")

    # Apply the 2-opt heuristic to improve the tour
    tour = two_opt(tour, points)

    # Calculate and print the total distance of the optimized tour
    distance = total_distance(tour, points)
    logger.info(msg=f"Optimized tour: {tour}")
    logger.info(msg=f"Total distance: {distance}")

if __name__ == "__main__":
    main()
