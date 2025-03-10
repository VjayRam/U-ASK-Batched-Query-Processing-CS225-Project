from typing import List, Dict, Tuple, Set, Any, Hashable
from dataclasses import dataclass
import numpy as np
from scipy.cluster.hierarchy import fcluster, linkage
from queries.power import POWERQueryProcessor
from collections import Counter, defaultdict
from itertools import chain
import heapq
import json

@dataclass
class SpatialQuery:
    """
    Represents a spatial query with location, keywords, and other parameters.
    
    Attributes:
        query_id (int): Unique identifier for the query.
        location (Tuple[float, float]): Latitude and longitude of the query location.
        positive_keywords (List[str]): List of keywords that should be present in the results.
        negative_keywords (List[str]): List of keywords that should not be present in the results.
        k (int): Number of top results to return.
        lambda_factor (float): Weight factor between spatial and textual relevance.
    """
    query_id: int
    location: Tuple[float, float]
    positive_keywords: List[str]
    negative_keywords: List[str]
    k: int
    lambda_factor: float
    
    def __post_init__(self):
        # Convert to sets for faster lookups
        self.positive_set = set(self.positive_keywords)
        self.negative_set = set(self.negative_keywords)

class BatchPOWERQueryProcessor(POWERQueryProcessor):
    """
    Extension of POWERQueryProcessor for batch processing of queries
    using Grouped Query Batching (GQB) approach - optimized for performance
    """
    def __init__(self, teq_index, location_threshold: float = 10.0, keyword_similarity_threshold: float = 0.5):
        super().__init__(teq_index)
        self.location_threshold = location_threshold
        self.keyword_similarity_threshold = keyword_similarity_threshold
        # Cache for object keywords to avoid repeated dictionary lookups
        self.keyword_cache = {}

    def _calculate_keyword_similarity(self, set1: Set[str], set2: Set[str]) -> float:
        """Calculate Jaccard similarity between two keyword sets (optimized)"""
        if not set1 and not set2:
            return 1.0  # Both empty sets are considered identical
        
        intersection_size = len(set1 & set2)  # Faster set intersection
        union_size = len(set1 | set2)  # Faster set union
        
        return intersection_size / union_size if union_size > 0 else 0.0

    def _cluster_locations(self, queries: List[SpatialQuery], max_cluster_size: int = None) -> Dict[int, List[SpatialQuery]]:
        """
        Group queries by spatial proximity using hierarchical clustering (optimized)
        
        Args:
            queries: List of SpatialQuery objects
            max_cluster_size: Optional maximum number of queries per cluster. If specified,
                             clustering will respect this limit by creating new clusters when needed.
        """
        if len(queries) <= 1:
            return {0: queries}

        # Extract locations for clustering
        locations = np.array([query.location for query in queries])
        
        # For small sets, use a faster direct calculation
        if len(queries) <= 25:
            # Simplified clustering for small sets
            clusters = {}
            for i, query1 in enumerate(queries):
                assigned = False
                for cluster_id, cluster_queries in clusters.items():
                    # Skip clusters that have reached max size limit
                    if max_cluster_size is not None and len(cluster_queries) >= max_cluster_size:
                        continue
                        
                    # Check if this query is close to any existing cluster
                    query2 = cluster_queries[0]  # Use first query in cluster as reference
                    distance = np.sqrt(np.sum((np.array(query1.location) - np.array(query2.location))**2))
                    if distance <= self.location_threshold:
                        clusters[cluster_id].append(query1)
                        assigned = True
                        break
                
                if not assigned:
                    # Create a new cluster
                    clusters[len(clusters)] = [query1]
            
            return clusters
        else:
            # For larger sets, use the original hierarchical clustering
            linkage_matrix = linkage(locations, method='complete')
            cluster_labels = fcluster(linkage_matrix, self.location_threshold, criterion='distance')
            
            # Group queries by cluster (using defaultdict for efficiency)
            clustered_queries = defaultdict(list)
            for query, cluster_id in zip(queries, cluster_labels):
                clustered_queries[cluster_id].append(query)
            
            # Post-process to respect max_cluster_size if specified
            if max_cluster_size is not None:
                final_clusters = {}
                new_cluster_id = 1
                
                for cluster_id, cluster_queries in clustered_queries.items():
                    # If cluster is within size limit, keep it as is
                    if len(cluster_queries) <= max_cluster_size:
                        final_clusters[new_cluster_id] = cluster_queries
                        new_cluster_id += 1
                    else:
                        # Split oversized cluster into smaller ones
                        for i in range(0, len(cluster_queries), max_cluster_size):
                            chunk = cluster_queries[i:i + max_cluster_size]
                            final_clusters[new_cluster_id] = chunk
                            new_cluster_id += 1
                
                return final_clusters
            
            return dict(clustered_queries)

    def _cluster_by_keywords(self, queries: List[SpatialQuery]) -> Dict[int, List[SpatialQuery]]:
        """Group queries by keyword similarity (optimized algorithm)"""
        if len(queries) <= 1:
            return {0: queries}
        
        # Precompute keyword sets and similarities matrix for efficiency
        similarity_matrix = {}
        
        # Build a graph where nodes are queries and edges represent similarity above threshold
        graph = defaultdict(list)
        
        for i in range(len(queries)):
            for j in range(i+1, len(queries)):
                # Calculate similarity between keyword sets
                similarity = self._calculate_keyword_similarity(
                    queries[i].positive_set, 
                    queries[j].positive_set
                )
                
                if similarity >= self.keyword_similarity_threshold:
                    graph[i].append(j)
                    graph[j].append(i)
        
        # Use connected components algorithm to find clusters
        visited = set()
        clusters = defaultdict(list)
        cluster_id = 0
        
        for i in range(len(queries)):
            if i in visited:
                continue
                
            # Start a new cluster with BFS
            queue = [i]
            visited.add(i)
            
            while queue:
                node = queue.pop(0)
                clusters[cluster_id].append(queries[node])
                
                for neighbor in graph[node]:
                    if neighbor not in visited:
                        visited.add(neighbor)
                        queue.append(neighbor)
            
            cluster_id += 1
        
        # If no connections found, each query is its own cluster
        if not clusters and queries:
            return {i: [query] for i, query in enumerate(queries)}
            
        return dict(clusters)

    def _group_queries(self, queries: List[SpatialQuery], max_cluster_size: int = None) -> Dict[int, List[SpatialQuery]]:
        """
        Group queries based on both spatial proximity and keyword similarity (optimized)
        
        Args:
            queries: List of SpatialQuery objects
            max_cluster_size: Optional maximum number of queries per cluster
        """
        # Early return for small query sets
        if len(queries) <= 1:
            return {0: queries}
            
        # First group by spatial proximity
        spatial_clusters = self._cluster_locations(queries, max_cluster_size)
        
        # Then, within each spatial cluster, group by keyword similarity
        final_clusters = {}
        cluster_id = 0
        
        for spatial_group in spatial_clusters.values():
            # Skip keyword clustering for small groups
            if len(spatial_group) <= 1:
                final_clusters[cluster_id] = spatial_group
                cluster_id += 1
                continue
                
            keyword_clusters = self._cluster_by_keywords(spatial_group)
            
            for keyword_group in keyword_clusters.values():
                final_clusters[cluster_id] = keyword_group
                cluster_id += 1
        
        return final_clusters

    def _get_unified_query_parameters(self, queries: List[SpatialQuery]) -> Tuple:
        """
        Create a unified query plan for a group of similar queries (optimized)
        Returns a tuple of (bounds, unified_positive_keywords, unified_negative_keywords)
        """
        # Fast path for single query
        if len(queries) == 1:
            query = queries[0]
            max_radius = query.lambda_factor * 100
            bounds = (
                query.location[0] - max_radius,
                query.location[1] - max_radius,
                query.location[0] + max_radius,
                query.location[1] + max_radius
            )
            return (bounds, query.positive_keywords, query.negative_keywords)
        
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
        
        # Combine all positive keywords from all queries
        unified_positive_keywords = set()
        for query in queries:
            unified_positive_keywords.update(query.positive_set)
        
        # Combine all negative keywords that are common across all queries
        common_negative_keywords = set()
        if queries and queries[0].negative_keywords:
            common_negative_keywords = queries[0].negative_set.copy()
            for query in queries[1:]:
                common_negative_keywords &= query.negative_set
        
        return (bounds, list(unified_positive_keywords), list(common_negative_keywords))

    def _get_hashable_key(self, obj_id: Any) -> str:
        """
        Convert any object ID to a hashable string representation
        This is a more robust solution that handles nested unhashable types
        """
        try:
            # If already hashable, use its string representation
            hash(obj_id)
            return str(obj_id)
        except TypeError:
            # For unhashable types, use JSON serialization to get a string
            try:
                return json.dumps(obj_id, sort_keys=True)
            except (TypeError, ValueError):
                # If JSON serialization fails, use string representation with type
                return f"{type(obj_id).__name__}_{id(obj_id)}"

    def _process_cluster(self, queries: List[SpatialQuery]) -> Dict[int, List[Tuple]]:
        """Process all queries in a cluster efficiently (optimized)"""
        # Fast path for single query
        if len(queries) == 1:
            query = queries[0]
            results = {}
            results[query.query_id] = self.process_query(
                query.location,
                query.positive_keywords,
                query.negative_keywords,
                query.k,
                query.lambda_factor
            )
            return results
        
        # Get unified query parameters
        bounds, unified_positive_keywords, unified_negative_keywords = self._get_unified_query_parameters(queries)
        unified_positive_set = set(unified_positive_keywords)
        unified_negative_set = set(unified_negative_keywords)
        
        # Get all candidates in the expanded area
        found_objects = []
        self.teq_index.spatial_index.query_range(bounds, found_objects)
        
        # Efficient pre-filtering using sets
        candidates = {}
        for obj_id in found_objects:
            # Create a string key for the cache
            cache_key = self._get_hashable_key(obj_id)
            
            # Get object and cache its keywords
            if cache_key not in self.keyword_cache:
                try:
                    obj = self.teq_index.objects[obj_id]
                    self.keyword_cache[cache_key] = {
                        'obj': obj,
                        'keywords': set(obj['keywords'])
                    }
                except (KeyError, TypeError) as e:
                    # Skip this object if we can't access it
                    continue
                    
            cached_data = self.keyword_cache[cache_key]
            obj = cached_data['obj']
            obj_keywords = cached_data['keywords']
            
            # Skip objects with unified negative keywords
            if any(kw in obj_keywords for kw in unified_negative_set):
                continue
                
            # Include objects with at least one unified positive keyword
            if any(kw in obj_keywords for kw in unified_positive_set):
                candidates[obj_id] = obj
        
        # Early exit if no candidates found
        if not candidates:
            return {query.query_id: [] for query in queries}
        
        # Process each query using shared candidates
        results = {}
        for query in queries:
            # Use a heap for efficient top-k tracking
            top_k_heap = []
            
            # Query-specific filtering
            for obj_id, obj in candidates.items():
                # Get cached keywords using cache key
                cache_key = self._get_hashable_key(obj_id)
                
                # Skip if not in cache (should not happen, but just in case)
                if cache_key not in self.keyword_cache:
                    continue
                    
                obj_keywords = self.keyword_cache[cache_key]['keywords']
                
                # Skip objects with query-specific negative keywords
                if any(kw in obj_keywords for kw in query.negative_set):
                    continue
                
                # Only include if it has at least one of the query's positive keywords
                if any(kw in obj_keywords for kw in query.positive_set):
                    spatial_score = 1 - self.compute_distance(query.location, obj['location']) / 100
                    textual_score = sum(1 for kw in query.positive_keywords if kw in obj_keywords)
                    combined_score = query.lambda_factor * spatial_score + (1 - query.lambda_factor) * textual_score
                    
                    # Use a min-heap to keep track of top-k results efficiently
                    if len(top_k_heap) < query.k:
                        heapq.heappush(top_k_heap, (combined_score, obj_id, obj['location'], obj['full_text']))
                    elif combined_score > top_k_heap[0][0]:
                        heapq.heappushpop(top_k_heap, (combined_score, obj_id, obj['location'], obj['full_text']))
            
            # Convert heap to sorted list of results
            top_k_results = sorted(top_k_heap, key=lambda x: -x[0])
            results[query.query_id] = top_k_results
            
        return results

    def process_batch_queries(self, queries: List[Dict], max_cluster_size: int = None) -> Dict[int, List[Tuple]]:
        """
        Process multiple queries efficiently using optimized Grouped Query Batching (GQB)
        
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
            max_cluster_size: Optional maximum number of queries per cluster.
                             Controls how queries are grouped for batch processing.
        
        Returns:
            Dictionary mapping query_id to results
        """
        # Early exit for empty queries
        if not queries:
            return {}
            
        # Fast path for single query
        if len(queries) == 1:
            q = queries[0]
            query_id = q.get('query_id', 0)
            results = self.process_query(
                q['location'],
                q['positive_keywords'],
                q['negative_keywords'],
                q['k'],
                q['lambda_factor']
            )
            return {query_id: results}
        
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
        
        # Group queries by both spatial proximity and keyword similarity
        grouped_queries = self._group_queries(spatial_queries, max_cluster_size)
        
        # Process each group with a unified query plan
        all_results = {}
        for _, group_queries in grouped_queries.items():
            group_results = self._process_cluster(group_queries)
            all_results.update(group_results)
            
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
