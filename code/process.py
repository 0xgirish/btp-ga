import argparse
import subprocess
import pickle
import logging

import osm
import numpy as np
import pandas as pd
from geopy.distance import geodesic


# eculedian and geodistance
edistance, gdistance = lambda u, v: np.sqrt(np.sum((u-v)**2)), lambda u, v: geodesic(set(u), set(v))

# set logging level
logging.basicConfig(level=logging.INFO)

# process region osm file
def process(region):
    # create region direactory
    subprocess.run(['mkdir', '-p', f'csv/{region}'])

    # extract data from osm file
    osmHandler = osm.OSMHandler(region)
    osmHandler.apply_file(f'region/{region}.osm')

    # save extracted data to csv files
    osmHandler.save()

# xytransform transforms the region coordinates to xy
def xytransform(region):
    # get data for region
    df = pd.read_csv(f'csv/{region}/shops.csv')
    with open(f'csv/{region}/obstacles.pk', 'rb') as obsfile:
        obstacles = pickle.load(obsfile)

    # get metadata for region, e.g. minimum and maximum coordinates
    with open(f'csv/{region}/meta.txt', 'r') as metafile:
        metadata = np.array(list(map(float, metafile.readlines())))

    # calculate ratios mean
    ratios, size = list(), df.shape[0]
    for i in range(size):
        u = df.iloc[i]
        for j in range(i+1, size):
            v = df.iloc[j]
            e, g = edistance(u, v), gdistance(u, v).km
            ratios.append(g/e)
    constant = pd.Series(ratios).mean()
    logging.info(f"ratios mean = {constant}")

    # transform restaurants coordinates
    transformed = constant * df
    transformed.to_csv(f'csv/{region}/shops.xy.csv', index=False)

    # transform obstacles coordinates
    tobstacles = obstacles * constant
    tobstacles.dump(f'csv/{region}/obstacles.xy.pk')

    # transform metadata
    tmetadate = metadata * constant
    with open(f'csv/{region}/meta.xy.txt', 'w')  as metafile:
        for data in tmetadate:
            print(data, file=metafile)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-region', '--region', help='region to process', type=str)
    parser.add_argument('-process', '--process', help='type of preprocessing, e.g. osm, xy')

    args = parser.parse_args()

    if args.process == 'osm':
        process(args.region)
    elif args.process == 'xy':
        xytransform(args.region)
    else:
        print('invalid process argument')
