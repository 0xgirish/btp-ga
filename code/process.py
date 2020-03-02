import argparse
import subprocess

import osm
import numpy as np
import pandas as pd
from geopy.distance import geodesic


# eculedian and geodistance
edistance, gdistance = lambda u, v: np.sqrt(np.sum((u-v)**2)), lambda u, v: geodesic(set(u), set(v))

# process region osm file
def process(region):
    # create region direactory
    subprocess.run(['mkdir', '-p', f'csv/{region}'])

    # extract data from osm file
    osmHandler = osm.OSMHandler(region)
    osmHandler.apply_file(f'region/{region}.osm')

    # save extracted data to csv files
    osmHandler.save()

    # trasform lat, lon to xy coordinates
    xytransform(region, osmHandler)

# handler contains information about maximum and minimum lat, lon of the area
def xytransform(region, handler):
    df = pd.read_csv(f'csv/{region}/shops.csv')

    ratios, size = list(), df.shape[0]
    for i in range(size):
        u = df.iloc[i]
        for j in range(i+1, size):
            v = df.iloc[j]
            e, g = edistance(u, v), gdistance(u, v).km
            ratios.append(g/e)

    constants = pd.Series(ratios)
    transformed = constants.mean() * df
    transformed.to_csv(f'csv/{region}/shops.xy.csv', index=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-region', '--region', help='process osm file', type=str)
    region = parser.parse_args().region

    process(region)
