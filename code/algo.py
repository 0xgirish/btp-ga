import logging
import random
import numpy as np
from sklearn.cluster import KMeans
from collections import defaultdict
from multiprocessing import Pool
from sympy.geometry.line import Segment2D


import constants
import geometry
from util import node_fitness

# set logging level
logging.basicConfig(level=logging.INFO)

class Model():
    instance = None # instance is the coordinates of the restaurants
    obstacles = None # enviorment obstacles
    radius = None # radius is the distance a fully charged drone can travel from recharging station and come back with payload
    n_circles = None # number of charging stations to cover restaurants
    lat_range, lon_range = None, None # range of lattitude and longitude

    def __init__(self, gnome=None, log=False):
        np.random.seed(seed=constants.SEED)
        if Model.instance is None:
            raise Exception('please initialize the model class first, e.g. Run Mode.Init(instance, radius, n_circles)')

        self.log = log
        if gnome is None:
            kmeans = KMeans(n_clusters=Model.n_circles, random_state=0).fit(Model.instance.values)
            self.centers = kmeans.cluster_centers_
            # lats = np.random.uniform(Model.lat_range[0], Model.lat_range[1], Model.n_circles)
            # lons = np.random.uniform(Model.lon_range[0], Model.lon_range[1], Model.n_circles)
            # self.centers = np.column_stack((lats, lons))
        else:
            self.centers = gnome

    # fitness of the chromosome is covered_nodes_percentage - overlaped_nodes_percentage
    def fitness(self):
        n_nodes = Model.instance.shape[0]
        args = [(center, Model.instance, Model.radius) for center in self.centers]
        with Pool(len(self.centers)) as pool:
            results = pool.starmap(node_fitness, args)
            pool.join() # wait until all functions finish
            covered = np.array([0 for _ in range(n_nodes)])
            for result in results:
                covered += result

        covered_nodes_percentage = 100 * np.sum(covered != 0) / n_nodes
        overlaped_nodes_percentage = 100 * np.sum(covered > 1) / n_nodes
        print(f'covered_nodes -> {covered_nodes_percentage} overlaped_nodes -> {overlaped_nodes_percentage}')
        
        return (covered_nodes_percentage - overlaped_nodes_percentage)


    def __str__(self):
        return f'{self.centers}'

    @classmethod
    def Init(cls, instance, radius, n_circles, obstacles):
        geometry.init(obstacles)
        cls.instance = instance
        cls.obstacles = obstacles
        cls.radius = radius
        cls.n_circles = n_circles

        data = instance.values
        lat_max, lon_max = np.max(data[:, 0]), np.max(data[:, 1])
        lat_min, lon_min = np.min(data[:, 0]), np.min(data[:, 1])

        cls.lat_range = np.array([lat_min, lat_max])
        cls.lon_range = np.array([lon_min, lon_max])

    @classmethod
    def selection(cls, population):
        fit_models_copy = []
        fit_models = population[0:round(constants.SELECTION_PERCENTAGE * constants.POPULATION)]

        for model in fit_models:
            fit_models_copy.append(Model(gnome=model.centers.copy()))

        return fit_models_copy

    @classmethod
    def crossover(cls, object1, object2):
        centers1, centers2 = object1.centers.copy(), object2.centers.copy()

        for i in range(Model.n_circles):
            if np.random.uniform(0, 1) <= constants.CROSSOVER_PROBABILITY:
                centers1[i], centers2[i] = centers2[i], centers1[i]

        return Model(gnome=centers1) if random.randint(0,1) == 0 else Model(gnome=centers2)


    @classmethod
    def mutation(cls, obj):
        centers = obj.centers.copy()

        for i in range(Model.n_circles):
            if np.random.uniform(0, 1) <= constants.MUTATION_PROBABILITY:
                if constants.MUTATION_DISTRIBTION == "uniform":
                    centers[i] += np.random.uniform(-constants.MUTATION_RANGE, constants.MUTATION_RANGE, 2)
                else:
                    centers[i] += np.random.normal(0, constants.MUTATION_RANGE, 2)

        return Model(gnome=centers)

    @classmethod
    def new_generation(cls, population):
        new_gen = []
        elite_model = Model.selection(population)
        new_gen.extend(elite_model)
        top_units = len(new_gen)

        for i in range(top_units, constants.POPULATION):

            offspring = None
            if i == top_units:
                offspring = Model.crossover(elite_model[0], elite_model[1])
            elif i < constants.POPULATION - 2:
                parentA = random.randint(0, len(elite_model)-1)
                parentB = random.randint(0, len(elite_model)-1)

                offspring = Model.crossover(elite_model[parentA], elite_model[parentB])
            else:
                parentA = random.randint(0, len(elite_model)-1)
                offspring = elite_model[parentA]

            offspring = Model.mutation(offspring)
            new_gen.append(offspring)

        return new_gen
