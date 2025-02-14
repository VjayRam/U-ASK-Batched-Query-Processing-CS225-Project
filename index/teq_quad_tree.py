from typing import Dict, List, Tuple
import hashlib
import pandas as pd

class Location:
    def __init__(self, lat: float, lon: float):
        self.lat = lat
        self.lon = lon

class SpatioTextualObject:
    def __init__(self, id: str, location: Location, text: str, keywords: List[str],weights: List[float]):
        self.id = id
        self.location = location
        self.text = text 
        self.keywords = keywords
        self.weights = weights

class TEQNode:
    def __init__(self, boundary: Tuple[float, float, float, float], max_objects: int = 30000):
        # Boundary: (min_lat, min_lon, max_lat, max_lon)
        self.boundary = boundary
        self.max_objects = max_objects
         
        # Four components of TEQ leaf cell
        self.ltp = None  # Location Table Pointer
        self.neigh = []  # Neighbor List
        self.iti = {}    # Inverted Textual Index
        self.oti = {}    # Object Text Index
        
        # Quadtree components
        self.objects = []
        self.children = [None, None, None, None]  # NW, NE, SW, SE
        self.is_leaf = True

class TEQIndex:
    def __init__(self, boundary: Tuple[float, float, float, float], max_depth: int = 15, max_objects: int = 30000):
        self.spatial_index = TEQNode(boundary, max_objects)
        self.max_depth = max_depth
        
    def insert(self, obj: SpatioTextualObject, depth: int = 0):
        def _insert_at_node(node: TEQNode, obj: SpatioTextualObject, depth: int):
            if not self._in_boundary(node.boundary, obj.location):
                return False
                
            if node.is_leaf:
                if len(node.objects) < node.max_objects or depth >= self.max_depth:
                    node.objects.append(obj)
                    return True
                else:
                    # Split node
                    self._split_node(node)
                    return self._insert_after_split(node, obj, depth)
            else:
                # Try inserting into children
                for child in node.children:
                    if child and _insert_at_node(child, obj, depth + 1):
                        return True
            return False
            
        return _insert_at_node(self.spatial_index, obj, depth)
    
    def build_textual_index(self):
        """Second pass: Build textual indexes"""
        def _build_leaf_indexes(node: TEQNode):
            if node.is_leaf and node.objects:
                # Build inverted textual index (iti)
                for obj in node.objects:
                    words = self._tokenize(obj.text)
                    for word in words:
                        if word not in node.iti:
                            node.iti[word] = {
                                'size': 0,
                                'max_weight': 0.0,
                                'list_ptr': self._create_list_pointer(word),
                                'set_ptr': self._create_set_pointer(word)
                            }
                        # Update statistics
                        node.iti[word]['size'] += 1
                        weight = self._calculate_weight(word, obj.text)
                        node.iti[word]['max_weight'] = max(
                            node.iti[word]['max_weight'], 
                            weight
                        )
                        
                # Build object text index (oti)
                for obj in node.objects:
                    node.oti[obj.id] = self._store_text(obj.text)
            
            # Recurse on children
            if not node.is_leaf:
                for child in node.children:
                    if child:
                        _build_leaf_indexes(child)
                        
        _build_leaf_indexes(self.spatial_index)

    def _split_node(self, node: TEQNode):
        """Split a node into four children"""
        min_lat, min_lon, max_lat, max_lon = node.boundary
        mid_lat = (min_lat + max_lat) / 2
        mid_lon = (min_lon + max_lon) / 2
        
        # Create four children with appropriate boundaries
        node.children[0] = TEQNode((min_lat, min_lon, mid_lat, mid_lon), node.max_objects)  # NW
        node.children[1] = TEQNode((min_lat, mid_lon, mid_lat, max_lon), node.max_objects)  # NE
        node.children[2] = TEQNode((mid_lat, min_lon, max_lat, mid_lon), node.max_objects)  # SW
        node.children[3] = TEQNode((mid_lat, mid_lon, max_lat, max_lon), node.max_objects)  # SE
        
        node.is_leaf = False

    def _calculate_weight(self, word: str, text: str) -> float:
        """Calculate word weight (e.g., TF-IDF or relative frequency)"""
        words = self._tokenize(text)
        return words.count(word) / len(words)

    def _tokenize(self, text: str) -> List[str]:
        """Basic text tokenization"""
        return text.lower().split()

    def _in_boundary(self, boundary: Tuple[float, float, float, float], location: Location) -> bool:
        """Check if location is within boundary"""
        min_lat, min_lon, max_lat, max_lon = boundary
        return (min_lat <= location.lat <= max_lat and 
                min_lon <= location.lon <= max_lon)

    def _create_list_pointer(self, word: str) -> str:
        """Create pointer for inverted list file"""
        return f"list_{hashlib.md5(word.encode()).hexdigest()}"

    def _create_set_pointer(self, word: str) -> str:
        """Create pointer for inverted set file"""
        return f"set_{hashlib.md5(word.encode()).hexdigest()}"

    def _store_text(self, text: str) -> str:
        """Store text and return pointer"""
        return f"text_{hashlib.md5(text.encode()).hexdigest()}"




def build_teqnode_from_csv(data: pd.DataFrame, boundary: Tuple[float, float, float, float]= [-90,90,-180,180], max_objects: int = 30000) -> TEQNode:
    teq_node = TEQIndex(boundary, max_objects)
    print("Building TEQ Node")
    try:
        for _, row in data.iterrows():
            location = Location(row['Latitude'], row['Longitude'])
            obj = SpatioTextualObject(row['ObjectID'], location, row['FullText'],weights=row['Weights'],keywords=row['Keywords'])
            teq_node.insert(obj)
            
        print("TEQ Node Built",teq_node)
        return teq_node
    except Exception as e:
        print(f"Error: {e}")
