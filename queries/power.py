import heapq
from math import sqrt


class POWERQueryProcessor:
    """
    A class to process spatial and textual queries using a combination of spatial and textual scores.
    Attributes:
    -----------
    teq_index : object
        An index object that provides candidate objects based on location and keywords.
    Methods:
    --------
    __init__(teq_index):
        Initializes the query processor with the given index.
    compute_distance(loc1, loc2):
        Computes the Euclidean distance between two locations.
    count_keyword_matches(keywords, positive_keywords):
        Counts the number of positive keywords that match the given keywords.
    process_query(location, positive_keywords, negative_keywords, k, lambda_factor=0.5):
        Processes the query by combining spatial and textual scores and returns the top-k results.
    """

    def __init__(self, teq_index):
        self.teq_index = teq_index
    
    def compute_distance(self, loc1, loc2):
        return sqrt((loc1[0] - loc2[0]) ** 2 + (loc1[1] - loc2[1]) ** 2)
    
    def count_keyword_matches(self, keywords, positive_keywords):
        return sum(1 for word in positive_keywords if word in keywords)
    
    def process_query(self, location, positive_keywords, negative_keywords, k, lambda_factor=0.5):
        candidates = self.teq_index.get_candidates(location, positive_keywords, negative_keywords)
        
        heap = []
        for obj_id in candidates:
            obj = self.teq_index.objects[obj_id]
            spatial_score = 1 - self.compute_distance(location, obj['location']) / 100
            textual_score = self.count_keyword_matches(obj['keywords'], positive_keywords)
            score = lambda_factor * spatial_score + (1 - lambda_factor) * textual_score
            heapq.heappush(heap, (-score, obj_id, obj['location'], obj['full_text']))
        
        return [heapq.heappop(heap) for _ in range(min(k, len(heap)))]
