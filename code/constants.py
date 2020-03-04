# constants for the geneatic algorithm
SEED = None
RADIUS, N_CIRCLES, POPULATION, SELECTION_PERCENTAGE, EPOCHS = None, None, None, None, 100
MUTATION_PROBABILITY, MUTATION_RANGE, MUTATION_DISTRIBTION, CROSSOVER_PROBABILITY = None, None, None, None

# change seed
def change_seed(seed):
    global SEED
    SEED = seed

# region cdg
def cdg():
    global RADIUS, N_CIRCLES, POPULATION, SELECTION_PERCENTAGE
    global MUTATION_PROBABILITY, MUTATION_RANGE, MUTATION_DISTRIBTION, CROSSOVER_PROBABILITY 
    RADIUS = 1
    N_CIRCLES = 4
    POPULATION = 40
    SELECTION_PERCENTAGE = 0.35
    MUTATION_PROBABILITY = 0.05
    CROSSOVER_PROBABILITY = 0.6
    MUTATION_RANGE = 0.06
    MUTATION_DISTRIBTION = "normal"


# region dlh
def dlh():
    global RADIUS, N_CIRCLES, POPULATION, SELECTION_PERCENTAGE
    global MUTATION_PROBABILITY, MUTATION_RANGE, MUTATION_DISTRIBTION, CROSSOVER_PROBABILITY 
    RADIUS = 4
    N_CIRCLES = 10
    POPULATION = 40
    SELECTION_PERCENTAGE = 0.35
    MUTATION_PROBABILITY = 0.05
    CROSSOVER_PROBABILITY = 0.6
    MUTATION_RANGE = 0.04
    MUTATION_DISTRIBTION = "normal"


# region blr
def blr():
    global RADIUS, N_CIRCLES, POPULATION, SELECTION_PERCENTAGE
    global MUTATION_PROBABILITY, MUTATION_RANGE, MUTATION_DISTRIBTION, CROSSOVER_PROBABILITY 
    RADIUS = 4
    N_CIRCLES = 12
    POPULATION = 40
    SELECTION_PERCENTAGE = 0.35
    MUTATION_PROBABILITY = 0.05
    CROSSOVER_PROBABILITY = 0.6
    MUTATION_RANGE = 0.036
    MUTATION_DISTRIBTION = "uniform"


# initialize constants according to experiment region
def initialize(region, tag):
    assert region in ['cdg', 'dlh', 'blr']
    if region == 'cdg':
        cdg()
    elif region == 'dlh':
        dlh()
    else:
        blr()

    with open(f'experiments/#{tag}/config.txt', 'w') as config:
        print(f'SEED = {SEED}', file=config)
        print(f'RADIUS = {RADIUS}', file=config)
        print(f'N_CIRCLES = {N_CIRCLES}', file=config)
        print(f'POPULATION = {POPULATION}', file=config)
        print(f'SELECTION_PERCENTAGE = {SELECTION_PERCENTAGE}', file=config)
        print(f'MUTATION_PROBABILITY = {MUTATION_PROBABILITY}', file=config)
        print(f'CROSSOVER_PROBABILITY = {CROSSOVER_PROBABILITY}', file=config)
        print(f'MUTATION_RANGE = {MUTATION_RANGE}', file=config)
        print(f'MUTATION_DISTRIBTION = "{MUTATION_DISTRIBTION}"', file=config)
