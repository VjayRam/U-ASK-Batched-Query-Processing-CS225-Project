import time
    
class POWER_BF:
    def __init__(self, index):
        self.index = index

    def process_query(self, query):
        powerbf_time = time.time()
        nearest_idxs = self.index.spatial_index.query(query["location"], k=query["k"])[1]
        
        # Convert KDTree index to ObjectID
        object_ids = [self.index.index_to_objectid[idx] for idx in nearest_idxs if idx < len(self.index.index_to_objectid)]

        # Safely retrieve objects
        candidates = [self.index.objects[obj_id] for obj_id in object_ids if obj_id in self.index.objects]

        # Apply AND filter
        and_filtered = [obj for obj in candidates if all(kw in obj.Keywords for kw in query["and_keywords"])]

        # Apply OR filter
        or_filtered = [obj for obj in and_filtered if any(kw in obj.Keywords for kw in query["or_keywords"])]

        # Apply negative keyword filtering
        final_results = [obj for obj in or_filtered if not any(kw in obj.Keywords for kw in query["negative_keywords"])]

        print("Query Processed by POWER_BF")
        print(f"POWER_BF Query Time: {time.time() - powerbf_time}")
        return final_results[:query["k"]]

