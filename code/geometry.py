from queue import Queue
import networkx as nx

from typing import List

from sympy import Point, Polygon, convex_hull
from sympy.geometry import Segment
from sympy.geometry.line import Segment2D
from sympy.geometry.util import intersection

from osm import Obstacles

EMPTY = list()
POLYGONS = None

def init(obstacles: Obstacles):
    POLYGONS = obstacles.polygons()

class SegmentVector(Segment):
    def __init__(self, from: Point, to: Point):
        if POLYGONS is None:
            raise Exception("call geometry.init before using it")
        super().__init__(from, to)
        self.from, self.to = from, to

    @classmethod
    def from_segment(s: Segment) -> SegmentVector:
        return SegmentVector(s.p1, s.p2)

    # intersection finds polygons which intersects with the segment
    def intersection(self) -> List[Polygon]:
        intersected_polygons = list()
        for polygon in POLYGONS:
            intersect = intersection(self, polygon)
            if intersect == EMPTY or any(isinstance(item, Segment2D) for item in intersect):
                continue

            intersected_polygons.append(polygon)

        return intersected_polygons

    # convexpath add segment which does not intersects to graph g
    # other segments to queue q
    def convexpath(self, polygons: List[Polygon], q: Queue, g: nx.Graph) -> List[Polygon]:
        for polygon in polygons:
            points = polygon.vertices
            points.extend([self.from, self.to])
            hull = convex_hull(*points, polygon=True)
            
            for side in hull.sides:
                segment = SegmentVector.from_segment(side)
                if segment.intersection() == EMPTY:
                    g.add_edge(segment.p1, segment.p2, float(segment.length))
                else:
                    q.put(segment)

    # calculate ESP distance
    def esp(self) -> float:
        q, g = Queue(), nx.Graph()
        q.put(self)
        
        while not q.empty():
            segment = q.get()
            polygons = segment.intersection()
            if polygons == EMPTY:
                continue
            segment.convexpath(polygons, q, g)

        length, _ = g.bidirectional_dijkstra(self.from, self.to)
        return length
