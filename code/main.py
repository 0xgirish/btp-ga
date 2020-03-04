import subprocess
import argparse
import logging
import pickle

import pandas as pd
import matplotlib.pyplot as plt
import constants
from algo import Model
from util import draw_gacluster

# config logging
logging.basicConfig(level=logging.INFO)

def main(region, tag):
    # load obstacles, obstacles.xy.pk
    with open(f'csv/{region}/obstacles.xy.pk', 'rb') as obsfile:
        obstacles = pickle.load(obsfile)

    # load region instance
    df = pd.read_csv(f'csv/{region}/shops.xy.csv')

    # initialize constants
    constants.initialize(region, tag)

    Model.Init(df, constants.RADIUS, constants.N_CIRCLES, obstacles)
    models = [Model() for _ in range(constants.POPULATION)]
    fitness_per_iteration, best_model = list(), None

    for iteration in range(constants.EPOCHS):
        fitness = [model.fitness() for model in models]
        model_fitness = zip(fitness, models)
        model_fitness = sorted(model_fitness, key=lambda k: k[0], reverse=True)
        fitness_per_iteration.append(model_fitness[0][0])
        population = []

        for j in range(constants.POPULATION):
            population.append(model_fitness[j][1])

        models = Model.new_generation(population)
        best_model = model_fitness[0][1].centers
        logging.info(f'\titerations: {iteration}, fitness: {model_fitness[0][0]}')

    pd.DataFrame(best_model, columns=['lat', 'lon']).to_csv(f'experiment/#{tag}/csv/centers.{region}.csv', index=False)

    plt.plot([i for i in range(constants.EPOCHS)], fitness_per_iteration)
    plt.xlabel('iterations')
    plt.ylabel('best fitness')
    plt.savefig(f'experiments/#{tag}/fig/{region}.iteration.png', format='png')

    draw_gacluster(df, region, tag, obstacles)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-exp-tag', '--tag', help='experiment tag to organize results', type=str)
    parser.add_argument('-region', '--region', help='name of the region for data', type=str)

    args = parser.parse_args()
    subprocess.run(['mkdir', '-p', f'experiments/#{args.tag}/csv', f'experiments/#{args.tag}/csv'])

    main(args.region, args.tag)
