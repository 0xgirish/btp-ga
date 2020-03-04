from multiprocessing import Pool
from math import floor, ceil
from util import Pair
from sympy.geometry.line import Segment2D

import argparse
import logging
import pickle
import subprocess
import geometry
import pandas as pd
import numpy as np

# logging config
logging.basicConfig(level=logging.INFO)

shops, polygons = None, None
esp_mapping = dict()

# compute esp for center and all shops
def compute(center):
    global shops, polygons, esp_mapping
    
    for shop in shops.values:
        segment, pair = Segment2D(shop, center), Pair(shop, center)
        esp_mapping[pair.hash()] = geometry.esp(segment)

    logging.info(f'\tesp calculation completed for {center}')

def main(region):
    global shops, metadata, polygons
    shops = pd.read_csv(f'csv/{region}/shops.xy.csv')
    # get meta data
    with open(f'csv/{region}/meta.xy.txt') as metafile:
        metadata = list(map(float, metafile.readlines()))

    with open(f'csv/{region}/polygons.xy.pk', 'rb') as obsfile:
        polygons = pickle.load(obsfile)

    geometry.init(polygons, is_polygon=True)

    minlat, minlon, maxlat, maxlon = metadata
    candidates = list()
    for lat in range(ceil(minlat), floor(maxlat)+1):
        for lon in range(ceil(minlon), floor(maxlon)+1):
            candidates.append((lat, lon))

    with Pool(144) as pool:
        pool.map(compute, candidates)
        pool.join()

    with open(f'esp/{region}/esp.pk', 'wb') as espfile:
        pickle.dump(esp_mapping, espfile)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-region', '--region', help='name of the region for data', type=str)

    args = parser.parse_args()
    subprocess.run(['mkdir', '-p', f'esp/{args.region}'])
    main(args.region)
