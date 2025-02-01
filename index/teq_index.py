from collections import defaultdict
from scipy.spatial import KDTree
import time

class TEQIndex:
    def __init__(self):
        self.spatial_index = None
        self.textual_index = defaultdict(set)
        self.objects = {}  # Store object by ObjectID
        self.index_to_objectid = []  # Store mapping from KDTree index to ObjectID

    def build_index(self, data):
        teq_time = time.time()
        print("Building TEQ Index")
        locations = []
        self.index_to_objectid = []
        
        for _, row in data.iterrows():
            obj_id = row.ObjectID
            self.objects[obj_id] = row  # Store objects by ID
            locations.append((row.Latitude, row.Longitude))
            self.index_to_objectid.append(obj_id)  # Maintain order
        
        self.spatial_index = KDTree(locations)  # Build KDTree
        print("TEQ Index Built")
        print(f"TEQ Index Time: {time.time() - teq_time}")

