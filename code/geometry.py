import logging
import networkx as nx

from queue import Queue
from typing import List, Dict
from collections import defaultdict

from sympy import Point, Polygon, convex_hull
from sympy.geometry.line import Segment2D
from sympy.geometry.util import intersection as segment_intersection

from osm import Obstacles

# set logging level
logging.basicConfig(level=logging.INFO)

EMPTY = list()
POLYGONS = None

def init(obstacles: Obstacles):
    global POLYGONS
    if POLYGONS is not None:
        logging.warning('geometry.py: can not initialize obstacles again')
        return

    POLYGONS = obstacles.polygons()
    logging.info("obstacles initialized")

# intersection finds polygons which intersects with the segment
def intersection(segment: Segment2D) -> List[Polygon]:
    intersected_polygons = list()
    for polygon in POLYGONS:
        intersect = segment_intersection(segment, polygon)
        if intersect == EMPTY or any(isinstance(item, Segment2D) for item in intersect):
            continue
        intersected_polygons.append(polygon)

    return intersected_polygons

# convexpath add all the segments of convex hull to queue, except visited segments
def convexpath(segment: Segment2D, polygons: List[Polygon], q: Queue, visited: Dict[Segment2D, bool]):
    # get convex hull for source, destination and vertices of polygon
    for polygon in polygons:
        points = polygon.vertices
        points.extend([segment.p1, segment.p2])
        hull = convex_hull(*points, polygon=True)
        
        for side in hull.sides:
            if not visited[side]:
                q.put(side)

# calculate Euclidean Shortest Path (ESP) distance, ref: Hong & Murry (2013)
def esp(segment: Segment2D) -> float:
    q, g, visited = Queue(), nx.Graph(), defaultdict(bool)

    q.put(segment)
    while not q.empty():
        segment = q.get()
        if not visited[segment]:
            visited[segment] = True

        polygons = intersection(segment)
        if polygons == EMPTY:
            g.add_edge(segment.p1, segment.p2, weight = float(segment.length))
            continue
        convexpath(segment, polygons, q, visited)

    length, _ = nx.bidirectional_dijkstra(g, segment.p1, segment.p2)
    return length
