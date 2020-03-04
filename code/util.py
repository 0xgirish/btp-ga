import logging
import seaborn as sns
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sympy.geometry.line import Segment2D
import geometry

# logging config
logging.basicConfig(level=logging.INFO)

# Pool the results for multiprocessing, returns covered nodes
def node_fitness(center, instance, radius):
    n_nodes = instance.shape[0]
    covered = np.array([0 for _ in range(n_nodes)])
    nodes = instance.values
    for i in range(n_nodes):
        segment = Segment2D(nodes[i], center)
        if geometry.esp(segment) <= radius:
            covered[i] = 1
        logging.info(f'\tnode {i} for center: {center} completed')

    logging.info(f'node_fitness for {center} completed')

    return covered

def draw_gacluster(df, region, tag, obstacles):
    geometry.init(obstacles)
    centers = pd.read_csv(f'experiments/#{tag}/csv/centers.{region}.csv').values
    
    Model.Init(df, constants.RADIUS, constants.N_CIRCLES)
    model = Model(gnome=centers, log=True)
    print(model.fitness())

    Y = [i for i in range(len(centers))]
    y = [len(centers) for i in range(df.shape[0])]
    nodes = df.values[:, 1:]
    for i in range(df.shape[0]):
        for j in range(len(centers)):
            segment = Segment2D(nodes[i], centers[j])
            if geometry.esp(segment) <= Model.radius:
                y[i] = j
                break

    sns.scatterplot(x="lat", y="lon", data=df, hue=y)
    plt.plot(centers[:, 0], centers[:, 1], 'o')
    plt.savefig(f'experiments/#{tag}/fig/{region}.gacluster.png', format='png')
