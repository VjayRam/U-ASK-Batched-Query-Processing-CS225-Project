import time

class POWER:
    def __init__(self, index):
        self.index = index

    def process_query(self, query):
        power_time = time.time()
        nearest_idxs = self.index.spatial_index.query(query["location"], k=query["k"])[1]
        
        # Convert KDTree index to ObjectID
        object_ids = [self.index.index_to_objectid[idx] for idx in nearest_idxs]

        candidates = [self.index.objects[obj_id] for obj_id in object_ids if obj_id in self.index.objects]

        # Apply filtering for positive and negative keywords
        filtered_candidates = [obj for obj in candidates if any(kw in obj.Keywords for kw in query["positive_keywords"])]
        final_results = [obj for obj in filtered_candidates if not any(kw in obj.Keywords for kw in query["negative_keywords"])]
        print("Query Processed by POWER")
        print(f"POWER Query Time: {time.time() - power_time}")
        return final_results[:query["k"]]
