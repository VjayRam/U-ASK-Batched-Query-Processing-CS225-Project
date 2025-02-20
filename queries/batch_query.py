from typing import List, Dict, Tuple, Set
from dataclasses import dataclass
import numpy as np
from scipy.cluster.hierarchy import fcluster, linkage
from queries.power import POWERQueryProcessor

@dataclass
class SpatialQuery:
    query_id: int
    location: Tuple[float, float]
    positive_keywords: List[str]
    negative_keywords: List[str]
    k: int
    lambda_factor: float

class BatchPOWERQueryProcessor(POWERQueryProcessor):
    """
    Extension of POWERQueryProcessor for batch processing of spatially clustered queries
    """
    def __init__(self, teq_index, location_threshold: float = 10.0):
        super().__init__(teq_index)
        self.location_threshold = location_threshold

    def _cluster_locations(self, queries: List[SpatialQuery]) -> Dict[int, List[SpatialQuery]]:
        """Group queries by spatial proximity using hierarchical clustering"""
        if len(queries) < 2:
            return {0: queries}

        # Extract locations for clustering
        locations = np.array([query.location for query in queries])
        
        # Perform hierarchical clustering
        linkage_matrix = linkage(locations, method='complete')
        clusters = fcluster(linkage_matrix, self.location_threshold, criterion='distance')
        
        # Group queries by cluster
        clustered_queries: Dict[int, List[SpatialQuery]] = {}
        for query, cluster_id in zip(queries, clusters):
            if cluster_id not in clustered_queries:
                clustered_queries[cluster_id] = []
            clustered_queries[cluster_id].append(query)
            
        return clustered_queries

    def _process_cluster(self, queries: List[SpatialQuery]) -> Dict[int, List[Tuple]]:
        """Process all queries in a spatial cluster efficiently"""
        # Find bounding box for all queries in cluster
        locations = np.array([query.location for query in queries])
        min_lat, min_lon = np.min(locations, axis=0)
        max_lat, max_lon = np.max(locations, axis=0)
        
        # Expand bounding box by maximum search radius
        max_radius = max(query.lambda_factor * 100 for query in queries)
        bounds = (
            min_lat - max_radius,
            min_lon - max_radius,
            max_lat + max_radius,
            max_lon + max_radius
        )
        
        # Get all candidates in the expanded area
        found_objects = []
        self.teq_index.spatial_index.query_range(bounds, found_objects)
        
        # Process each query using shared candidates
        results = {}
        for query in queries:
            # Use parent class methods for consistent processing
            candidates = self.teq_index.get_candidates(
                query.location,
                query.positive_keywords,
                query.negative_keywords
            )
            
            results[query.query_id] = self.process_query(
                query.location,
                query.positive_keywords,
                query.negative_keywords,
                query.k,
                query.lambda_factor
            )
            
        return results

    def process_batch_queries(self, queries: List[Dict]) -> Dict[int, List[Tuple]]:
        """
        Process multiple queries efficiently by grouping spatially close queries
        
        Args:
            queries: List of query dictionaries, each containing:
                    {
                        'query_id': int,
                        'location': (lat, lon),
                        'positive_keywords': list of keywords,
                        'negative_keywords': list of keywords,
                        'k': int,
                        'lambda_factor': float
                    }
        
        Returns:
            Dictionary mapping query_id to results
        """
        # Convert queries to SpatialQuery objects
        spatial_queries = [
            SpatialQuery(
                query_id=q.get('query_id', i),
                location=q['location'],
                positive_keywords=q['positive_keywords'],
                negative_keywords=q['negative_keywords'],
                k=q['k'],
                lambda_factor=q['lambda_factor']
            )
            for i, q in enumerate(queries)
        ]
        
        # Cluster queries by location
        clustered_queries = self._cluster_locations(spatial_queries)
        
        # Process each cluster
        all_results = {}
        for cluster_id, cluster_queries in clustered_queries.items():
            cluster_results = self._process_cluster(cluster_queries)
            all_results.update(cluster_results)
            
        return all_results

def create_batch_queries(locations: List[Tuple[float, float]], 
                        keywords: List[List[str]], 
                        k: int = 5, 
                        lambda_factor: float = 0.5) -> List[Dict]:
    """
    Helper function to create batch queries from locations and keywords
    
    Args:
        locations: List of (lat, lon) tuples
        keywords: List of keyword lists for each query
        k: Number of results to return per query
        lambda_factor: Weight between spatial and textual relevance
    
    Returns:
        List of query dictionaries ready for batch processing
    """
    queries = []
    for i, (location, kw_list) in enumerate(zip(locations, keywords)):
        queries.append({
            'query_id': i,
            'location': location,
            'positive_keywords': kw_list,
            'negative_keywords': [],  # Can be customized if needed
            'k': k,
            'lambda_factor': lambda_factor
        })
    return queries
