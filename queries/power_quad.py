import heapq
from math import sqrt
from typing import List

from index.teq_quad_tree import TEQIndex

class POWERQueryProcessor:
    def __init__(self, teq_index: TEQIndex):
        self.teq_index = teq_index
    
    def compute_distance(self, loc1, loc2):
        return sqrt((loc1[0] - loc2[0]) ** 2 + (loc1[1] - loc2[1]) ** 2)
    
    def count_keyword_matches(self, keywords: List[str], positive_keywords: List[str]) -> int:
        """Count how many keywords from positive_keywords are in the object's keywords."""
        return sum(1 for word in positive_keywords if word in keywords)
    
    def process_query(self, location, positive_keywords, negative_keywords, k, lambda_factor=0.5):
        # Retrieve candidates based on spatial and textual indices
        spatial_candidates = self._query_spatial_index(location)
        textual_candidates = self._query_textual_index(positive_keywords, negative_keywords)
        
        # Combine spatial and textual candidates (intersection could be used)
        candidates = list(set(spatial_candidates).intersection(set(textual_candidates)))
        
        # Score candidates and push to a heap
        heap = []
        for obj_id in candidates:
            obj = self.teq_index.spatial_index.oti.get(obj_id)
            spatial_score = 1 - self.compute_distance(location, obj.location) / 100
            textual_score = self.count_keyword_matches(obj.keywords, positive_keywords)
            score = lambda_factor * spatial_score + (1 - lambda_factor) * textual_score
            heapq.heappush(heap, (-score, obj_id))
        
        # Return top-k candidates
        print(heap)
        return [heapq.heappop(heap)[1] for _ in range(min(k, len(heap)))]

    def _query_spatial_index(self, location):
        """Query the spatial index to retrieve candidates within a certain range."""
        # In a real scenario, this would be more sophisticated (e.g., range query or k-nearest neighbors)
        print("spatial",[obj.id for obj in self.teq_index.spatial_index.objects if self._in_range(location, obj.location)])
        return [obj.id for obj in self.teq_index.spatial_index.objects if self._in_range(location, obj.location)]
    
    def _query_textual_index(self, positive_keywords, negative_keywords):
        """Query the textual index to retrieve candidates that match the positive and negative keywords."""
        matched_objects = []
        # Loop through the inverted index and find matching objects for positive keywords
        for word in positive_keywords:
            if word in self.teq_index.spatial_index.iti:
                for obj_id in self.teq_index.spatial_index.iti[word]['list_ptr']:
                    matched_objects.append(obj_id)
        
        # Exclude objects matching negative keywords
        filtered_objects = [obj_id for obj_id in matched_objects if not self._has_negative_keywords(obj_id, negative_keywords)]
        print("filtered_objects",filtered_objects)
        return filtered_objects
    
    def _in_range(self, location1, location2, range_distance=100):
        """Check if two locations are within a given range."""
        return self.compute_distance(location1, location2) <= range_distance
    
    def _has_negative_keywords(self, obj_id, negative_keywords):
        """Check if an object contains any negative keywords."""
        obj = self.teq_index.spatial_index.oti.get(obj_id)
        return any(neg_kw in obj.keywords for neg_kw in negative_keywords)
