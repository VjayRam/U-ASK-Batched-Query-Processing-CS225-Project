import sys
from typing import List, Tuple, Optional

sys.setrecursionlimit(10**6)

class QuadtreeNode:
    """
    A class representing a node in a quadtree structure.
    Attributes:
    -----------
    bounds : tuple
        A tuple representing the bounds of the node in the format (x_min, y_min, x_max, y_max).
    capacity : int
        The maximum number of objects a node can hold before it needs to subdivide.
    objects : list
        A list storing objects in the format (obj_id, location, keywords, full_text).
    children : list or None
        A list of child QuadtreeNode objects if the node has been subdivided, otherwise None.
    Methods:
    --------
    __init__(bounds, capacity=4):
        Initializes a QuadtreeNode with given bounds and capacity.
    subdivide():
        Subdivides the current node into four child nodes.
    insert(obj_id, location, keywords, full_text):
        Inserts an object into the quadtree. Returns True if the object is inserted, otherwise False.
    query_range(bounds, found_objects):
        Queries the quadtree for objects within a given range and appends them to found_objects.
    """
    __slots__ = ('bounds', 'capacity', 'objects', 'children')  # Optimize memory usage
    
    def __init__(self, bounds: Tuple[float, float, float, float], capacity: int = 1000):
        self.bounds = bounds  # (x_min, y_min, x_max, y_max)
        self.capacity = capacity  # Increased capacity to reduce tree depth
        self.objects: List[Tuple] = []
        self.children: Optional[List['QuadtreeNode']] = None
    
    def subdivide(self):
        x_min, y_min, x_max, y_max = self.bounds
        mid_x = (x_min + x_max) / 2
        mid_y = (y_min + y_max) / 2
        
        # Create children only when needed
        self.children = [
            QuadtreeNode((x_min, y_min, mid_x, mid_y), self.capacity),
            QuadtreeNode((mid_x, y_min, x_max, mid_y), self.capacity),
            QuadtreeNode((x_min, mid_y, mid_x, y_max), self.capacity),
            QuadtreeNode((mid_x, mid_y, x_max, y_max), self.capacity)
        ]
        
        # Redistribute existing objects to children
        for obj in self.objects:
            for child in self.children:
                if child.insert(obj[0], obj[1], obj[2], obj[3]):
                    break
        self.objects.clear()  # Clear objects after redistribution
    
    def insert(self, obj_id, location, keywords, full_text):
        if not (self.bounds[0] <= location[0] <= self.bounds[2] and 
                self.bounds[1] <= location[1] <= self.bounds[3]):
            return False

        # If we have children, insert into appropriate child
        if self.children is not None:
            for child in self.children:
                if child.insert(obj_id, location, keywords, full_text):
                    return True
            return False

        # No children, add to current node
        self.objects.append((obj_id, location, keywords, full_text))
        
        # Only subdivide if we exceed capacity and the bounds are large enough
        if len(self.objects) > self.capacity:
            # Check if subdivision is meaningful (prevent infinite subdivision)
            x_min, y_min, x_max, y_max = self.bounds
            if (x_max - x_min) > 0.0001 and (y_max - y_min) > 0.0001:
                self.subdivide()
            
        return True

    def query_range(self, bounds, found_objects):
        # Quick boundary check
        if not self._bounds_intersect(bounds):
            return

        # Add objects from current node
        found_objects.extend(obj for obj in self.objects 
                           if self._point_in_bounds(obj[1], bounds))

        # Recurse into children if they exist
        if self.children is not None:
            for child in self.children:
                child.query_range(bounds, found_objects)
    
    def _bounds_intersect(self, bounds) -> bool:
        return not (bounds[2] < self.bounds[0] or 
                   bounds[0] > self.bounds[2] or 
                   bounds[3] < self.bounds[1] or 
                   bounds[1] > self.bounds[3])
    
    @staticmethod
    def _point_in_bounds(point, bounds) -> bool:
        return (bounds[0] <= point[0] <= bounds[2] and 
                bounds[1] <= point[1] <= bounds[3])