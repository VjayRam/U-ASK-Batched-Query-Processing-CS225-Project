from collections import defaultdict
from scipy.spatial import KDTree
import time

class TEQIndex:
    """
    This class provides methods to analyze and visualize the results of spatial computing queries.

    Methods:
    build_index(data): Builds the spatial and textual index from the provided data.
    """
    def __init__(self):
        self.spatial_index = None
        self.textual_index = defaultdict(set)
        self.objects = {}  
        self.index_to_objectid = []  

    def build_index(self, data):
        teq_time = time.time()
        print("Building TEQ Index")
        locations = []
        self.index_to_objectid = []
        
        for _, row in data.iterrows():
            obj_id = row.ObjectID
            self.objects[obj_id] = row  
            locations.append((row.Latitude, row.Longitude))
            self.index_to_objectid.append(obj_id)  
        
        self.spatial_index = KDTree(locations)  
        print("TEQ Index Built")
        print(f"TEQ Index Time: {time.time() - teq_time}")

