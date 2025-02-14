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
    def __init__(self, bounds, capacity=4):
        self.bounds = bounds  # (x_min, y_min, x_max, y_max)
        self.capacity = capacity
        self.objects = []  # Stores (obj_id, location, keywords, full_text)
        self.children = None
    
    def subdivide(self):
        x_min, y_min, x_max, y_max = self.bounds
        
        
        mid_x = (x_min + x_max) / 2
        mid_y = (y_min + y_max) / 2

        self.children = [
            QuadtreeNode((x_min, y_min, mid_x, mid_y), self.capacity),  # Bottom-left
            QuadtreeNode((mid_x, y_min, x_max, mid_y), self.capacity),  # Bottom-right
            QuadtreeNode((x_min, mid_y, mid_x, y_max), self.capacity),  # Top-left
            QuadtreeNode((mid_x, mid_y, x_max, y_max), self.capacity)   # Top-right
        ]


    
    def insert(self, obj_id, location, keywords, full_text):
    # Check if the object is within the bounds of this node
        if not (self.bounds[0] <= location[0] <= self.bounds[2] and self.bounds[1] <= location[1] <= self.bounds[3]):
            return False  # Object is outside bounds
        
        if len(self.objects) < self.capacity and self.children is None:
            self.objects.append((obj_id, location, keywords, full_text))
            return True

        if self.children is None:
            self.subdivide()
        
        for child in self.children:
            if child.insert(obj_id, location, keywords, full_text):
                return True

        return False

    
    def query_range(self, bounds, found_objects):
        x_min, y_min, x_max, y_max = self.bounds
        q_x_min, q_y_min, q_x_max, q_y_max = bounds
        
        if q_x_max < x_min or q_x_min > x_max or q_y_max < y_min or q_y_min > y_max:
            return  # No overlap
        
        for obj in self.objects:
            found_objects.append(obj)
        
        if self.children is not None:
            for child in self.children:
                child.query_range(bounds, found_objects)