import time
    
# Boolean Range Query
class RangeQuery:
    def __init__(self, index):
        self.index = index
    
    def process_query(self, query):
        range_time = time.time()
        range_idxs = self.index.spatial_index.query_ball_point(query["location"], query["radius"])
        object_ids = [self.index.index_to_objectid[idx] for idx in range_idxs if idx < len(self.index.index_to_objectid)]
        candidates = [self.index.objects[obj_id] for obj_id in object_ids if obj_id in self.index.objects]
        final_results = [obj for obj in candidates if not any(kw in obj.Keywords for kw in query["negative_keywords"])]
        print("Query Processed by RangeQuery")
        print(f"RangeQuery Time: {time.time() - range_time}")
        return final_results