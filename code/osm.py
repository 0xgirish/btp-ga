import sys
import pickle

import osmium as osm
import numpy as np
import pandas as pd

from typing import List
from sympy import Polygon

FLOAT_MAX = sys.float_info.max

# An obstacle contains nodes (lat, lon) which forms a polygon and has height >= 12
class Obstacle:
    def __init__(self, nodes, node_map=None):
        if node_map is None:
            self.nodes = nodes
            return

        self.nodes = list()
        for node in nodes:
            self.nodes.append(node_map[node.ref])

    def __mul__(self, n):
        nodes = list()
        for i in range(len(self.nodes)):
            nodes.append(self.nodes[i] * n)
        return Obstacle(nodes)

    # draw the polygon with nodes on the figure
    def draw(self, fig):
        # TODO: draw logic here
        pass

class Obstacles:
    def __init__(self, region):
        self.region = region
        self.obstacles = list()

    def add(self, obstacle):
        self.obstacles.append(obstacle)

    def __mul__(self, n):
        new = Obstacles(self.region)
        for obstacle in self.obstacles:
            new.add(obstacle * n)
        return new

    # create polygons from Obstacles
    def polygons(obstacles: Obstacles) -> List[Polygon]:
        polygons = list()
        for obstacle in obstacles:
            polygons(Polygon(*obstacle.nodes))
        return polygons

    # iterator for obstacles
    def __iter__(self):
        for obstacle in self.obstacles:
            yield obstacle

    # dump to pickle file
    def dump(self, path):
        with open(path, 'wb') as obsfile:
            pickle.dump(self, obsfile)

    # save obstacles to pickle and txt file
    def save(self):
        # save obstacles to pickle file
        self.dump(f'csv/{self.region}/obstacles.pk')

        # save obstacles coordinates to txt file
        with open(f'csv/{self.region}/obstacles.txt', 'w') as obsfile:
            for obstacle in self.obstacles:
                print(obstacle.nodes, file=obsfile)

# OSMHandler extract restaurant's locations from the osm file and obstacles
class OSMHandler(osm.SimpleHandler):
    def __init__(self, region=None):
        osm.SimpleHandler.__init__(self)
        self.region = region
        self.minlat, self.minlon = FLOAT_MAX, FLOAT_MAX
        self.maxlat, self.maxlon = -1, -1
        self.osm_data, self.obstacles = list(), Obstacles(region) # contains list of all the building which have height >= 12 m
        self.node_location_map = dict()

    # add nodes which are restaurants
    def node(self, n):
        location = OSMHandler.getLocation(n.location)
        self.node_location_map[n.id] = location

        self.minlat = location[0] if location[0] < self.minlat else self.minlat
        self.minlon = location[1] if location[1] < self.minlon else self.minlon
        self.maxlat = location[0] if location[0] > self.maxlat else self.maxlat
        self.maxlon = location[1] if location[1] > self.maxlon else self.maxlon
        if OSMHandler.is_restaurant(n):
            self.osm_data.append(location)

    # check for buildings with height greater then 12m
    def way(self, w):
        if OSMHandler.is_obstacle(w):
            self.obstacles.add(Obstacle(w.nodes, self.node_location_map))

    # create csv file for shops and obstacles
    def save(self):
        # save restaurants coordinates
        data_columns = ['lat', 'lon']
        df = pd.DataFrame(self.osm_data, columns=data_columns)
        df.to_csv(f'csv/{self.region}/shops.csv', index=False)

        # save obstacles to pickle and txt file
        self.obstacles.save()

        # save maximum and minimum coordinates in the region
        with open(f'csv/{self.region}/meta.txt', 'w') as metafile:
            print(self.minlat, file=metafile)
            print(self.minlon, file=metafile)
            print(self.maxlat, file=metafile)
            print(self.maxlon, file=metafile)

    @staticmethod
    def is_obstacle(w):
        for tag in w.tags:
            if tag.k == 'building:height' and float(tag.v) >= 12:
                return True and w.is_closed()
        return False

    @staticmethod
    def is_restaurant(elem):
        for tag in elem.tags:
            if tag.v == 'restaurant':
                return True
        return False

    @staticmethod
    def getLocation(location):
        return np.array([float(location.lat), float(location.lon)])

