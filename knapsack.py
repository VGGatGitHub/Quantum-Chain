#to test the code run:> python ./knapsack.py -d H_Beds.csv -t 150000 -n 3 
 
#node can be a city, hospital, distribution center, store, or etc.

#capacity is the maximum content that can be allocated at the node
#e.g. sick people, people it can serve, vaccines or products it can hold;

#status is the currently utilized capacity of the product in percentage %

#impact value - the main parameter to be optimized for:
# e.g.: GDP, health,  nutrition, or social 	measure


from pprint import pprint
from typing import List, Dict
from math import log, ceil
import argparse

import pandas as pd
#from dwave.system import LeapHybridSampler
import dimod
import neal



def knapsack_bqm(cities, values, weights, total_capacity, value_r=0, weight_r=0):
    """
    build the knapsack binary quadratic model
    
    From DWave Knapsack examples
    Originally from Andrew Lucas, NP-hard combinatorial problems as Ising spin glasses
    Workshop on Classical and Quantum Optimization; ETH Zuerich - August 20, 2014
    based on Lucas, Frontiers in Physics _2, 5 (2014) 

    See # Q-Alpha version for original introduction of value_r and weight_r
    
        value_r: the proportion of value contributed from the objects outside of the knapsack. 
                For the standard knapsack problem this is 0,
                but in the case of GDP a closed city retains some % of GDP value;
                or for health problems it may contribute negative value (-1).
                
        weight_r: the proportion of weight contributed from the objects outside of the knapsack. 
                For the standard knapsack problem this is 0,
                but in the case of sick people we might consider that a closed city
                retains some % of its sick people over time;
                or for health problems it may contribute negative value (-1)
   
    """

    # Initialize BQM - use large-capacity BQM so that the problem can be
    # scaled by the user.
    bqm = dimod.AdjVectorBQM(dimod.Vartype.BINARY)

    # Lagrangian multiplier
    # First guess as suggested in Lucas's paper
    lagrange = max(values)

    # Number of objects
    x_size = len(values)

    # Lucas's algorithm introduces additional slack variables to handle
    # the inequality. max_y_index indicates the maximum index in the y
    # sum; hence the number of slack variables.
    max_y_index = ceil(log(total_capacity))

    # Slack variable list for Lucas's algorithm. The last variable has
    # a special value because it terminates the sequence.
    y = [2**n for n in range(max_y_index - 1)]
    y.append(total_capacity + 1 - 2**(max_y_index - 1))

    # Q-Alpha - calculate the extra constant in second part of problem hamiltonian
    C = sum([weight * weight_r for weight in weights])
    
    # Q-Alpha - change weights to weight*(1-weight_r)
    weights = [weight*(1-weight_r) for weight in weights]

    # Q-Alpha - change values to value*(1-value_r)
    values = [value*(1-value_r) for value in values]

    # Hamiltonian xi-xi terms
    for k in range(x_size):
        # Q-Alpha add final term lagrange * C * weights[k]
        bqm.set_linear(
            cities[k],
            lagrange * (weights[k] ** 2) - values[k] + lagrange * C * weights[k])

    # Hamiltonian xi-xj terms
    for i in range(x_size):
        for j in range(i + 1, x_size):
            key = (cities[i], cities[j])
            bqm.quadratic[key] = 2 * lagrange * weights[i] * weights[j]

    # Hamiltonian y-y terms
    for k in range(max_y_index):
        # Q-Alpha add final term -lagrange * C * y[k]
        bqm.set_linear('y' + str(k), lagrange *
                       (y[k]**2) - lagrange * C * y[k])

    # Hamiltonian yi-yj terms
    for i in range(max_y_index):
        for j in range(i + 1, max_y_index):
            key = ('y' + str(i), 'y' + str(j))
            bqm.quadratic[key] = 2 * lagrange * y[i] * y[j]

    # Hamiltonian x-y terms
    for i in range(x_size):
        for j in range(max_y_index):
            key = (cities[i], 'y' + str(j))
            bqm.quadratic[key] = -2 * lagrange * weights[i] * y[j]

    return bqm


def solve_nodes(nodes: List, values: List, status: List, total_capacity: int,
                 value_r=0, weight_r=0, num_reads=1, verbose=False) -> Dict:
    """
    Solves problem: "Which cities should should be shut down in order to stay
    within healthcare resources constraints while maximizing overall GDP"
    parameters:
        nodes as cities - list of city names
        value as gdps -  list of GDP for each city
        status as sick - number of sick people within the city
        total_capacity - max capacity for sick people summed over all cities
        num_reads - number of samples to take
        verbose - whether to print out best result
    returns:
        (dict) - list of dictionaries with individual results and selected attributes
                    sorted in order of least energy (maximum value) first
    """
    sum_status=sum(status)
    if sum_status < total_capacity:

        print(f"Warning while solveing: Total utilized capacity needed {sum_status} is less ",
              f"than total capacity {total_capacity}. There's no knapsack problem to solve!")

    bqm = knapsack_bqm(nodes, values, status, total_capacity, value_r=value_r, weight_r=weight_r)

    #VGG sampler = LeapHybridSampler()
    sampler = neal.SimulatedAnnealingSampler()
    samplesets = [sampler.sample(bqm) for _ in range(num_reads)]

    df = pd.DataFrame({'node': nodes, 'value': values, 'status': status})
    df = df.set_index('node')

    solution_set = []
    for sampleset in samplesets:
        open_cities = []
        closed_cities = []
        for k, v in sampleset.first.sample.items():
            if k in nodes:
                if v == 1:
                    open_cities.append(k)
                else:
                    closed_cities.append(k)
        solution_set.append({
            'open_cities': open_cities,
            'closed_cities': closed_cities,
            'solution_indicator': sampleset.first.energy,
            'total_value': sum(df.loc[open_cities]['value']) + sum(df.loc[closed_cities]['value']) * value_r,
            'used_capacity': int(round(sum(df.loc[open_cities]['status'])))
        })

    # do sorting from lowest to highest energy (solution_indicator)
    if num_reads > 1:
        energies = [solution['solution_indicator'] for solution in solution_set]
        solution_set = [x for _, x in sorted(zip(energies, solution_set))]

    if verbose:
        print('\nBEST SOLUTION\n')
        print('nodes in the knapsack:')
        print(solution_set[0]['open_cities'])
        print('\n')
        print('nodes outside the knapsack:')
        print(solution_set[0]['closed_cities'])
        print('\n')
        total_value = sum(df['value'])
        solutin_value = solution_set[0]['total_value']
        print(
              f'Total Impact Value: {solutin_value} of {total_value} ({(100*solutin_value/total_value):.1f}%)')
        used_capacity = solution_set[0]['used_capacity']
        print(
            f'Used up capacity: {used_capacity:d} of {total_capacity} ({(100*used_capacity/total_capacity):.1f}%)')

        if num_reads > 1:
            print('\nNEXT BEST SOLUTION\n')
            print('nodes in the knapsack:')
            print(solution_set[1]['open_cities'])
            print('\n')
            print('nodes outside the knapsack:')
            print(solution_set[1]['closed_cities'])
            print('\n')
            total_value = sum(df['value'])
            solutin_value = solution_set[1]['total_value']
            print(
                f'Total Impact Value: {solutin_value} of {total_value} ({(100*solutin_value/total_value):.1f}%)')
            used_capacity = solution_set[1]['used_capacity']
            print(
                f'Used up capacity: {used_capacity:d} of {total_capacity} ({(100*used_capacity/total_capacity):.1f}%)')

    return solution_set


def solve_nodes_using_csv(filepath: str, total_capacity: int, value_r=0, weight_r=0,
                          num_reads=1, verbose=False) -> Dict:
    """
    Example: to solve for cities as nodes the given a csv file must be in the format:
    cities, gdps, and sick people where the cvs file needs to have the header: city, gdp, sick;
    In general the format will be: nodes,capacity,value,status; #VGG
    """
    df0 = pd.read_csv(filepath)
    
    #VGG update to the new data format of node, capacity, status
    #assert ','.join(df.columns) == 'node,value,status', "Ensure csv header is node,value,status"

    #assert ','.join(df.columns) == 'city,gdp,sick', "Ensure csv header is city,gdp,sick"
    #solution_set = solve_cities(list(df['city']), list(df['gdp']), list(df['sick']), total_capacity, 
    
    #"City","State","Total","Available","ICUs","Available_ICU"
    df1 = pd.DataFrame()
    df1['node']=df0['City']
    #df1['status']=abs(df0['ICUs']-df0['Available_ICU']) #number of sick people in the ICU
    df1['status']=(5*df0['ICUs']//5 +10*abs(df0['Total']-df0['ICUs'])//10) 
    #assume medical team of 5 and  vaccine efficiency 85%
    df1['value']=(5*(df0['ICUs']//5 +abs(df0['Total']-df0['Available']-df0['ICUs'])//10)*85)//100 
	
    df=df1[0:100] #consider 100 cities

    #VGG note the weight_r has to be selected so that the over all number of sick people is under the max. value
    
    solution_set = solve_nodes(list(df['node']), list(df['value']), list(df['status']), #list(df['capacity']),
        total_capacity, value_r=value_r, weight_r=weight_r, num_reads=num_reads, verbose=verbose)
    
    return solution_set


def main():
    """ CLI
    """
    description = "Solve the problem: \"Which nodes should be considerd to be in the knapsack "
    description += "in order to stay within the resource limits (capacity <= max capacity)"
    description += "while maximizing overall impact measure\""
    parser = argparse.ArgumentParser(description=description)
    
    parser.add_argument('--data', '-d',
                        help="path to csv file with columns: node, capacity, status [%]. Header expected")
    parser.add_argument('--total-capacity', '-t', type=int,
                        help="Maximum capacity for all nodes combined.")
    parser.add_argument('--num-reads', '-n', type=int, default=1,
                        help="Number of sample solutines to return")
                        
    args = parser.parse_args()
    
    solution_set = solve_nodes_using_csv(
        args.data, args.total_capacity, value_r=0.01, weight_r=0.02, 
        num_reads=args.num_reads, verbose=True) 
        #see the function knapsack_bqm for details 
        #for GDP use value_r=.8, weight_r=0.2
        #VGG note the weight_r has to be selected so that the over all number of sick people is under the max. value

#to test the code run:> python ./knapsack.py -d H_Beds.csv -t 150000 -n 3 

if __name__ == '__main__':
    main()
