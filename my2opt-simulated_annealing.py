# Solving Traveling Salesman Problem by applying Simulated Annealing
# Neighborhood structure/Move: 2-exchange (2-opt)
# - remove two arcs, not sharing a node -> three paths
# - reconnect the three paths and form a new dicycle, by inserting two arcs


# Constants
MYVERYBIGNUMBER = 424242424242 
MYVERYSMALLNUMBER = 1e-5
NUMBEROFCITIES = 100
INITIALTEMPERATURE = 2000.0    
COOLINGRATE = 0.9995

# Initialize random number generator 
import random
random.seed(42)

import matplotlib.pyplot as plt
import math

import logging
import sys
logger = logging.getLogger(name='sa-logger')
logging.basicConfig(level=logging.DEBUG,
                    format='[%(asctime)s] %(message)s',
                    handlers=[logging.FileHandler("sa.log"),logging.StreamHandler(stream=sys.stdout)])
logging.getLogger('matplotlib.font_manager').disabled = True

def define_tsp_instance():
    # Define a list of points (coordinates) for the TSP
    points = []
    for i in range(NUMBEROFCITIES):
        x = random.uniform(0,100)
        y = random.uniform(0,100)
        points.append((x,y))    

    # Separate the x and y values into separate lists
    x = [coord[0] for coord in points]
    y = [coord[1] for coord in points]

    """
    # Create a scatter plot for the instance
    plt.figure(1)
    plt.scatter(x, y)
    plt.xlabel('X-axis Label')
    plt.ylabel('Y-axis Label')
    plt.title(f'Instance of randomly generated TSP with {NUMBEROFCITIES} nodes')
    """
    
    return points, x, y

def euclidean_distance(point1, point2):
    x1, y1 = point1
    x2, y2 = point2
    return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5

def total_distance(tour, points):
    distance = 0
    for i in range(len(tour)):
        distance += euclidean_distance(points[tour[i]], points[tour[(i + 1) % len(tour)]])
    return distance

def create_random_tour(points, x, y):
    tour = list(range(len(points)))
    random.shuffle(tour)
    distance = total_distance(tour,points)

    # Create a line plot for the constructed tour
    plt.figure(2)
    plt.scatter(x, y)
    plt.xlabel('X-axis Label')
    plt.ylabel('Y-axis Label')
    for i in range(1, len(points)):
        x1, y1 = points[tour[i - 1]]
        x2, y2 = points[tour[i]]
        plt.plot([x1, x2], [y1, y2], 'b-')  # 'b-' specifies blue solid line
    x1, y1 = points[tour[len(points)-1]]
    x2, y2 = points[tour[0]]
    plt.plot([x1, x2], [y1, y2], 'b-')  # 'b-' specifies blue solid line
    plt.title(f'Initial solution: tour on {NUMBEROFCITIES} nodes, distance {distance:.2f}')

    return tour

def two_opt(tour, points, x, y):
    old_tour = tour
    tour_dist = total_distance(tour,points)
    logger.debug(msg=f"2-opt starts with tour having total distance: {tour_dist}")


    improved = True
    iteration = 0
    while improved:
        improved = False
        i = 1
        while ((i <= len(tour)-2) and not(improved)):
            j = i+1
            while((j <= len(tour)) and not(improved)): 
                if j - i == 1:
                    j += 1
                    continue  # No need to reverse two consecutive edges

                new_tour = tour[:]
                new_tour[i:j] = reversed(tour[i:j])
                if total_distance(new_tour, points) < total_distance(tour, points):
                    tour = new_tour
                    current_distance = total_distance(tour,points)
                    improved = True
                    logger.debug(msg=f"Iteration {iteration+1:3n}, distance (curr): {current_distance:.2f}")
                    iteration += 1
                j += 1
            i += 1

    # Create a line plot for the old tour and the 2-opt tour
    plt.figure(5)
    plt.scatter(x, y)
    plt.xlabel('X-axis Label')
    plt.ylabel('Y-axis Label')

    for i in range(1, len(points)):
        x1, y1 = points[old_tour[i - 1]]
        x2, y2 = points[old_tour[i]]
        plt.plot([x1, x2], [y1, y2], 'g-',linewidth=1)  
    x1, y1 = points[old_tour[len(points)-1]]
    x2, y2 = points[old_tour[0]]
    plt.plot([x1, x2], [y1, y2], 'g-',linewidth=1)  
    for i in range(1, len(points)):
        x1, y1 = points[tour[i - 1]]
        x2, y2 = points[tour[i]]
        plt.plot([x1, x2], [y1, y2], 'b-')  # 'b-' specifies blue solid line
    x1, y1 = points[tour[len(points)-1]]
    x2, y2 = points[tour[0]]
    plt.plot([x1, x2], [y1, y2], 'b-')  # 'b-' specifies blue solid line
    plt.title(f'Tours after applying 2-opt')

    logger.debug(msg=f"2-opt ends with tour having total distance: {tour_dist}")

    return tour, total_distance(tour, points) 

def simulated_annealing(tour, points, x, y):
    tour_dist = total_distance(tour,points)
    logger.debug(msg=f"SA starts with tour having total distance: {tour_dist}")

    iteration = 0

    # initialize data for maintaining history of objective values and temperature
    hist_curr_obj_vals = []
    hist_best_obj_vals = []
    hist_temp_vals = [] 

    # initialize current solution and best solution; become initial tour
    current_tour = tour 
    best_tour = tour    
    current_distance = total_distance(current_tour, points)
    best_distance = current_distance

    # initialize temperature
    temperature = INITIALTEMPERATURE 

    hist_curr_obj_vals.append(current_distance)
    hist_best_obj_vals.append(best_distance)
    hist_temp_vals.append(temperature)

    while temperature > MYVERYSMALLNUMBER:  # Cooling stops when temperature is close to 0
        while True:
            i, j = random.sample(range(len(current_tour)), 2)   # draw two random numbers i,j in {0,1,...,n-1}
            if (i>0) and (j > i+1):
                break
        
        # j > i+1, so the 2-exchange based on i and j is relevant 
        # remove arcs (i-1,i) and (j-1,j) and insert arcs (i-1,j-1) and (i,j)
        # resulting tour equals: 0->..->i-1->j-1->..->i->j->n-1->0 

        new_tour = current_tour[:i] + list(reversed(current_tour[i:j])) + current_tour[j:]
        new_distance = total_distance(new_tour, points)
        delta_distance = new_distance - current_distance

        if delta_distance < 0 or random.random() < math.exp(-delta_distance / temperature):
            current_tour = new_tour
            current_distance = new_distance

            if current_distance < best_distance:
                best_tour = current_tour
                best_distance = current_distance

        hist_curr_obj_vals.append(current_distance)
        hist_best_obj_vals.append(best_distance)
        hist_temp_vals.append(temperature)

        logger.debug(msg=f"Iteration {iteration+1:3n}, temp: {temperature:.2f}, distance (curr): {current_distance:.2f}, (best): {best_distance:.2f}")

        iteration += 1
        temperature *= COOLINGRATE

    # Create a line plot for the constructed tour
    plt.figure(3)
    plt.scatter(x, y)
    plt.xlabel('X-axis Label')
    plt.ylabel('Y-axis Label')
    for i in range(1, len(points)):
        x1, y1 = points[best_tour[i - 1]]
        x2, y2 = points[best_tour[i]]
        plt.plot([x1, x2], [y1, y2], 'b-')  # 'b-' specifies blue solid line
    x1, y1 = points[best_tour[len(points)-1]]
    x2, y2 = points[best_tour[0]]
    plt.plot([x1, x2], [y1, y2], 'b-')  # 'b-' specifies blue solid line
    plt.title(f'Best solution: tour on {NUMBEROFCITIES} nodes, distance {best_distance:.2f}')


    # Create a plot for the solution progress
    plt.figure(4)
    x = list(range(len(hist_curr_obj_vals)))
    y1 = [currobjval for currobjval in hist_curr_obj_vals]
    y2 = [bestobjval for bestobjval in hist_best_obj_vals]
    y3 = [tempval for tempval in hist_temp_vals]
    plt.plot(x, y1)
    plt.plot(x, y2)
    plt.plot(x, y3)

    plt.xlabel('Iteration')
    plt.ylabel('Distance')
    plt.title(f'Progress of simulated annealing applied to {len(tour)} nodes')

    return best_tour, best_distance

def main():
    # Create a TSP instance based on a given number of cities
    points, x, y = define_tsp_instance()
    
    # Create an initial tour (random permutation of points)
    tour = create_random_tour(points, x, y)

    # Apply simulated annealing to improve the tour
    sa_tour, sa_distance = simulated_annealing(tour, points, x, y)

    # Finally, apply 2-opt to make sure the tour is a local optimal solution
    optimized_tour, optimized_distance = two_opt(sa_tour, points, x, y)

    plt.show()

    print("Optimized tour:", optimized_tour)
    print("Total distance:", optimized_distance)

    
if __name__ == "__main__":
    main()


