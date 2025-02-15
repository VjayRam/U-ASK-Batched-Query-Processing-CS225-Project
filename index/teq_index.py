from models.quadtree import QuadtreeNode
import sys
from typing import Dict, Set, List, Tuple
from collections import defaultdict
import pickle
import os
import json
from datetime import datetime

sys.setrecursionlimit(10**6)

class TEQIndex:
    """_summary_
    A class to represent a spatial index using a quadtree structure.
    Attributes
    ----------
    spatial_index : QuadtreeNode
        The root node of the quadtree used for spatial indexing.
    objects : dict
        A dictionary to store objects with their metadata.
    Methods
    -------
    __init__(bounds):
        Initializes the TEQIndex with the given bounds.
    add_object(obj_id, location, keywords, full_text):
        Adds an object to the spatial index and stores its metadata.
    get_candidates(location, positive_keywords, negative_keywords, search_radius=10):
        Retrieves candidate objects within a search radius that match positive keywords and do not match negative keywords.
    """
     
    def __init__(self, bounds):
        self.spatial_index = QuadtreeNode(bounds, capacity=1000)
        self.objects: Dict = {}
        self._batch_buffer = defaultdict(list)
        self._buffer_size = 10000  # Adjust based on memory availability
        self.metadata = {
            'created_at': datetime.now().isoformat(),
            'bounds': bounds,
            'total_objects': 0
        }

    def add_object(self, obj_id: int, location: Tuple[float, float], 
                  keywords: List[str], full_text: str) -> None:
        """Add single object to index"""
        self.objects[obj_id] = {
            'location': location,
            'keywords': set(keywords),
            'full_text': full_text
        }
        self.spatial_index.insert(obj_id, location, keywords, full_text)
    
    def add_batch(self, batch: List[Tuple]) -> None:
        """Add multiple objects efficiently"""
        # Sort batch by location for more efficient insertion
        sorted_batch = sorted(batch, key=lambda x: (x[1][0], x[1][1]))
        
        # Process in smaller chunks for better memory management
        for obj_id, location, keywords, full_text in sorted_batch:
            self._batch_buffer[location].append((obj_id, keywords, full_text))
            
            if len(self._batch_buffer) >= self._buffer_size:
                self._flush_buffer()
        
        # Flush any remaining items
        if self._batch_buffer:
            self._flush_buffer()
    
    def _flush_buffer(self) -> None:
        """Insert buffered objects into the index"""
        for location, objects in self._batch_buffer.items():
            for obj_id, keywords, full_text in objects:
                self.objects[obj_id] = {
                    'location': location,
                    'keywords': set(keywords),
                    'full_text': full_text
                }
                self.spatial_index.insert(obj_id, location, keywords, full_text)
        
        self._batch_buffer.clear()
    
    def get_candidates(self, location: Tuple[float, float], 
                      positive_keywords: List[str], 
                      negative_keywords: List[str], 
                      search_radius: float = 10) -> Set[int]:
        # Ensure buffer is flushed before querying
        if self._batch_buffer:
            self._flush_buffer()
            
        x, y = location
        bounds = (x - search_radius, y - search_radius, 
                 x + search_radius, y + search_radius)
        
        found_objects: List = []
        self.spatial_index.query_range(bounds, found_objects)
        
        pos_keywords = set(positive_keywords)
        neg_keywords = set(negative_keywords)
        
        candidates = {
            obj_id for obj_id, _, keywords, _ in found_objects 
            if pos_keywords.intersection(keywords)
        }
        
        if neg_keywords:
            candidates = {
                obj_id for obj_id in candidates 
                if not neg_keywords.intersection(self.objects[obj_id]['keywords'])
            }
        
        return candidates

    def save_index(self, directory: str) -> None:
        """
        Save the index to disk
        Args:
            directory: Directory to save the index files
        """
        os.makedirs(directory, exist_ok=True)
        
        # Ensure all buffered items are inserted
        if self._batch_buffer:
            self._flush_buffer()
        
        # Update metadata
        self.metadata.update({
            'updated_at': datetime.now().isoformat(),
            'total_objects': len(self.objects)
        })
        
        # Save metadata
        with open(os.path.join(directory, 'metadata.json'), 'w') as f:
            json.dump(self.metadata, f, indent=2)
        
        # Save objects dictionary
        with open(os.path.join(directory, 'objects.pkl'), 'wb') as f:
            pickle.dump(self.objects, f, protocol=4)
        
        # Save spatial index
        with open(os.path.join(directory, 'spatial_index.pkl'), 'wb') as f:
            pickle.dump(self.spatial_index, f, protocol=4)
            
        print(f"Index saved to {directory}")
        print(f"Total objects: {self.metadata['total_objects']:,}")

    @classmethod
    def load_index(cls, directory: str) -> 'TEQIndex':
        """
        Load index from disk
        Args:
            directory: Directory containing the saved index files
        Returns:
            TEQIndex: Loaded index
        """
        # Load metadata
        with open(os.path.join(directory, 'metadata.json'), 'r') as f:
            metadata = json.load(f)
        
        # Create new instance
        index = cls(bounds=metadata['bounds'])
        index.metadata = metadata
        
        # Load objects
        with open(os.path.join(directory, 'objects.pkl'), 'rb') as f:
            index.objects = pickle.load(f)
        
        # Load spatial index
        with open(os.path.join(directory, 'spatial_index.pkl'), 'rb') as f:
            index.spatial_index = pickle.load(f)
        
        print(f"Index loaded from {directory}")
        print(f"Total objects: {metadata['total_objects']:,}")
        return index