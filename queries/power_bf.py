import time
    
class POWER_BF:
    """A class to process spatial queries using a brute-force approach.
    Attributes:
    -----------
    index : object
        An object containing spatial index, index to object ID mapping, and objects.
    Methods:
    --------
    __init__(index):
        Initializes the POWER_BF class with the given index.
    process_query(query):
        Processes the given query to find the nearest objects based on spatial location and applies keyword filters.
        Parameters:
            query (dict): A dictionary containing the query parameters:
                - location (tuple): The spatial location to query.
                - k (int): The number of nearest neighbors to retrieve.
                - and_keywords (list): A list of keywords that must be present in the objects.
                - or_keywords (list): A list of keywords where at least one must be present in the objects.
                - negative_keywords (list): A list of keywords that must not be present in the objects.
        Returns:
            list: A list of objects that match the query criteria.
    """
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

