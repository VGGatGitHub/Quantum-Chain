# Copyright [2020] [Quantum-Chain]
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from dwave_qbsolv import QBSolv
from dwave.system import LeapHybridSampler
import numpy as np
import matplotlib.pyplot as plt
import re
import pandas as pd
import geopandas

import math
import random

import dwavebinarycsp
import dwave.inspector
from dwave.system import EmbeddingComposite, DWaveSampler

from utilities import get_groupings, visualize_groupings, visualize_scatterplot

Total_Number_Cities = 21
Number_Deliveries = 3
cd = (int)(Total_Number_Cities/Number_Deliveries)

# Tunable parameters. 
A = 8500
B = 1
chainstrength = 4500
numruns = 100

## Custering Preprocess

class Coordinate:
    def __init__(self, x, y):
        self.x = x
        self.y = y

        # coordinate labels for groups red, green, and blue
        label = "{0},{1}_".format(x, y)
        self.r = label + "r"
        self.g = label + "g"
        self.b = label + "b"

def lat_lon_distance(a, b):
    """Calculates distance between two latitude-longitude coordinates."""
    R = 3963  # radius of Earth (miles)
    lat1, lon1 = math.radians(a[0]), math.radians(a[1])
    lat2, lon2 = math.radians(b[0]), math.radians(b[1])
    return math.acos(math.sin(lat1) * math.sin(lat2) +
                     math.cos(lat1) * math.cos(lat2) * math.cos(lon1 - lon2)) * R

def get_distance(a, b):
    R = 3963  # radius of Earth (miles)
    lat1, lon1 = math.radians(a.x), math.radians(b.x)
    lat2, lon2 = math.radians(a.y), math.radians(b.y)
    return math.acos(math.sin(lat1) * math.sin(lat2) +
                     math.cos(lat1) * math.cos(lat2) * math.cos(lon1 - lon2)) * R


def get_max_distance(coordinates):
    max_distance = 0
    for i, coord0 in enumerate(coordinates[:-1]):
        for coord1 in coordinates[i+1:]:
            distance = get_distance(coord0, coord1)
            max_distance = max(max_distance, distance)

    return max_distance


def cluster_points(scattered_points, filename):
    # Set up problem
    # Note: max_distance gets used in division later on. Hence, the max(.., 1)
    #   is used to prevent a division by zero
    coordinates = [Coordinate(x, y) for x, y in scattered_points]
    max_distance = max(get_max_distance(coordinates), 1)

    # Build constraints
    csp = dwavebinarycsp.ConstraintSatisfactionProblem(dwavebinarycsp.BINARY)

    # Apply constraint: coordinate can only be in one colour group
    choose_one_group = {(0, 0, 1), (0, 1, 0), (1, 0, 0)}
    for coord in coordinates:
        csp.add_constraint(choose_one_group, (coord.r, coord.g, coord.b))

    # Build initial BQM
    bqm = dwavebinarycsp.stitch(csp)

    # Edit BQM to bias for close together points to share the same color
    for i, coord0 in enumerate(coordinates[:-1]):
        for coord1 in coordinates[i+1:]:
            # Set up weight
            d = get_distance(coord0, coord1) / max_distance  # rescale distance
            weight = -math.cos(d*math.pi)

            # Apply weights to BQM
            bqm.add_interaction(coord0.r, coord1.r, weight)
            bqm.add_interaction(coord0.g, coord1.g, weight)
            bqm.add_interaction(coord0.b, coord1.b, weight)

    # Edit BQM to bias for far away points to have different colors
    for i, coord0 in enumerate(coordinates[:-1]):
        for coord1 in coordinates[i+1:]:
            # Set up weight
            # Note: rescaled and applied square root so that far off distances
            #   are all weighted approximately the same
            d = math.sqrt(get_distance(coord0, coord1) / max_distance)
            weight = -math.tanh(d) * 0.1

            # Apply weights to BQM
            bqm.add_interaction(coord0.r, coord1.b, weight)
            bqm.add_interaction(coord0.r, coord1.g, weight)
            bqm.add_interaction(coord0.b, coord1.r, weight)
            bqm.add_interaction(coord0.b, coord1.g, weight)
            bqm.add_interaction(coord0.g, coord1.r, weight)
            bqm.add_interaction(coord0.g, coord1.b, weight)

# Submit problem to D-Wave sampler
    sampler = EmbeddingComposite(DWaveSampler(solver={'qpu': True}))
    sampleset = sampler.sample(bqm, chain_strength=4, num_reads=1000)
    best_sample = sampleset.first.sample

    # Visualize graph problem
    dwave.inspector.show(bqm, sampleset)

    # Visualize solution
    groupings = get_groupings(best_sample)
    visualize_groupings(groupings, filename)
    return groupings
    # Print solution onto terminal
    # Note: This is simply a more compact version of 'best_sample'
    #print(groupings)
## Clustering Preprocess End

def plot_map(route,cities, cities_lookup,filename):

    data_list=[[key, cities[key][0], - cities[key][1]] for key in cities.keys()]
    df = pd.DataFrame(data_list)
    data_list=[[cities_lookup[route[i]], cities[cities_lookup[route[i]]][0], - cities[cities_lookup[route[i]]][1]] for i in range(cd)]
    df_visit = pd.DataFrame(data_list)
    
    #City,Latitude,Longitude
    df.columns=['City','Latitude','Longitude']
    df_visit.columns = ['City','Latitude','Longitude']
    df_start = df_visit[df_visit['City'].isin([cities_lookup[route[0]]])]  
    df_end = df_visit[df_visit['City'].isin([cities_lookup[route[0]]])]

    gdf_all = geopandas.GeoDataFrame(
        df, geometry=geopandas.points_from_xy(df.Longitude, df.Latitude))
    gdf_visit = geopandas.GeoDataFrame(
        df_visit, geometry=geopandas.points_from_xy(df_visit.Longitude, df_visit.Latitude))
    gdf_start = geopandas.GeoDataFrame(
        df_start, geometry=geopandas.points_from_xy(df_start.Longitude, df_start.Latitude))
    gdf_end = geopandas.GeoDataFrame(
        df_end, geometry=geopandas.points_from_xy(df_end.Longitude, df_end.Latitude))

    world = geopandas.read_file(
            geopandas.datasets.get_path('naturalearth_lowres'))

    # Restrict to the USA only.
    ax = world[world.name == 'United States of America'].plot(
        color='white', edgecolor='black')

    # plot the ``GeoDataFrame``
    x_values=gdf_visit.values.T[2]
    y_values=gdf_visit.values.T[1]
    plt.plot(x_values,y_values)

    gdf_all.plot(ax=ax, color='gray')
    gdf_visit.plot(ax=ax, color='blue')
    gdf_start.plot(ax=ax, color='green')
    gdf_end.plot(ax=ax, color='red')

    ax.set_xlim(xmin=-130, xmax=-65)
    ax.set_ylim(ymin=20, ymax=55)
    ax.set_yticks([])
    ax.set_xticks([])
    ax.set_aspect(1.2)

    ax.legend(['Path','All cites', 'To Visit','Start','End'])

    plt.savefig(filename)
    #plt.show()

cities = {
        'New York City': (40.72, 74.00),
        'Los Angeles': (34.05, 118.25),
        'Chicago': (41.88, 87.63),
        'Houston': (29.77, 95.38),
        'Phoenix': (33.45, 112.07),
        'Philadelphia': (39.95, 75.17),
        'San Antonio': (29.53, 98.47),
        'Dallas': (32.78, 96.80),
        'San Diego': (32.78, 117.15),
        'San Jose': (37.30, 121.87),
        'Detroit': (42.33, 83.05),
        'San Francisco': (37.78, 122.42),
        'Jacksonville': (30.32, 81.70),
        'Indianapolis': (39.78, 86.15),
        'Austin': (30.27, 97.77),
        'Columbus': (39.98, 82.98),
        'Fort Worth': (32.75, 97.33),
        'Charlotte': (35.23, 80.85),
        'Memphis': (35.12, 89.97),
        'Baltimore': (39.28, 76.62),
        'Columbus': (39.96, 82.99),
    }

cities_lookup = {
        0: 'New York City',
        1: 'Los Angeles',
        2: 'Chicago',
        3: 'Houston',
        4: 'Phoenix',
        5: 'Philadelphia',
        6: 'San Antonio',
        7: 'Dallas',
        8: 'San Diego',
        9: 'San Jose',
        10: 'Detroit',
        11: 'San Francisco',
        12: 'Jacksonville',
        13: 'Indianapolis',
        14: 'Austin',
        15: 'Columbus',
        16: 'Fort Worth',
        17: 'Charlotte',
        18: 'Memphis',
        19: 'Baltimore',
        20: 'Columbus',
    }

cities_index = {
        (40.72, 74.00) : 0,
        (34.05, 118.25) : 1,
        (41.88, 87.63) : 2,
        (29.77, 95.38) : 3,
        (33.45, 112.07): 4,
        (39.95, 75.17): 5,
        (29.53, 98.47): 6,
        (32.78, 96.80): 7,
        (32.78, 117.15): 8,
        (37.30, 121.87): 9,
        (42.33, 83.05): 10,
        (37.78, 122.42): 11,
        (30.32, 81.70): 12,
        (39.78, 86.15): 13,
        (30.27, 97.77): 14,
        (39.98, 82.98): 15,
        (32.75, 97.33): 16,
        (35.23, 80.85): 17,
        (35.12, 89.97): 18,
        (39.28, 76.62): 19,
        (39.96, 82.99): 20
    }

    # initial state, a randomly-ordered itinerary
init_state = list(cities.values())
random.shuffle(init_state)

#print("Init State")
#print(init_state)

clustered_filename = "twentyone_cities_clustered.png"
citygroups = cluster_points(init_state, clustered_filename)
citygroup_count = 0

for color, points in citygroups.items():
        
        # Ignore items that do not contain any coordinates
        if not points:
            continue

        pcount = 0

        points_array = np.array(points)
        points_len = len(points_array)
       

        D = [[0 for z in range(Total_Number_Cities)] for y in range(Total_Number_Cities)]

        for i in range(len(points_array)):
            if(i+1 < len(points_array)):
                x = points_array[i]
                y = points_array[i+1]
                citya = tuple(x.tolist())
                cityb = tuple(y.tolist())
                namea = cities_index[citya]
                nameb = cities_index[cityb]
                pcount = pcount + 1
                D[namea][nameb] = D[nameb][namea] = lat_lon_distance(citya,cityb)

        # Function to compute index in QUBO for variable 
        def return_QUBO_Index(a, b):
            return (a)*cd+(b)

        ## Creating the QUBO
        # Start with an empty QUBO
        Q = {}
        for i in range(cd*cd):
            for j in range(cd*cd):
                Q.update({(i,j): 0})

        # Constraint that each row has exactly one 1, constant = N*A
        for v in range(cd):
            for j in range(cd):
                Q[(return_QUBO_Index(v,j), return_QUBO_Index(v,j))] += -1*A
                for k in range(j+1, cd):
                    Q[(return_QUBO_Index(v,j), return_QUBO_Index(v,k))] += 2*A
                    Q[(return_QUBO_Index(v,k), return_QUBO_Index(v,j))] += 2*A

        # Constraint that each col has exactly one 1
        for j in range(cd):
            for v in range(cd):
                Q[(return_QUBO_Index(v,j), return_QUBO_Index(v,j))] += -1*A
                for w in range(v+1,cd):
                    Q[(return_QUBO_Index(v,j), return_QUBO_Index(w,j))] += 2*A
                    Q[(return_QUBO_Index(w,j), return_QUBO_Index(v,j))] += 2*A

        # Objective that minimizes distance
        for u in range(cd):
            for v in range(cd):
                if u!=v:
                    for j in range(cd):
                        Q[(return_QUBO_Index(u,j), return_QUBO_Index(v,(j+1)%cd))] += B*D[u][v]

        # Run the QUBO using qbsolv (classically solving)
        #resp = QBSolv().sample_qubo(Q)

        # Use LeapHybridSampler() for faster QPU access
        sampler = LeapHybridSampler()
        resp = sampler.sample_qubo(Q)

        # First solution is the lowest energy solution found
        sample = next(iter(resp))

        # Display energy for best solution found
        print('Energy: ', next(iter(resp.data())).energy)

        # Print route for solution found
        route = [-1]*cd
        for node in sample:
            if sample[node]>0:
                j = node%cd
                v = (node-j)/cd
                route[j] = int(v)

        # Compute and display total mileage
        mileage = 0
        for i in range(cd):
            mileage+=D[route[i]][route[(i+1)%cd]]

        print('Mileage: ', mileage)

        filename = "Hackathon_Route_Map_" + str(citygroup_count)
        citygroup_count = citygroup_count + 1
        plot_map(route,cities, cities_lookup, filename)

        # Print route:

        #for i in range(Total_Number_Cities):
            #print(cities_lookup[route[i]]+'\n')

        
