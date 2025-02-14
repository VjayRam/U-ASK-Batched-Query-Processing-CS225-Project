from models.quadtree import QuadtreeNode


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
        self.spatial_index = QuadtreeNode(bounds)
        self.objects = {}  

    def add_object(self, obj_id, location, keywords, full_text):
        self.objects[obj_id] = {'location': location, 'keywords': keywords, 'full_text': full_text}
        self.spatial_index.insert(obj_id, location, keywords, full_text)
    
    def get_candidates(self, location, positive_keywords, negative_keywords, search_radius=10):
        x, y = location
        bounds = (x - search_radius, y - search_radius, x + search_radius, y + search_radius)
        found_objects = []
        self.spatial_index.query_range(bounds, found_objects)
        
        candidates = {obj_id for obj_id, _, keywords, _ in found_objects if any(word in keywords for word in positive_keywords)}
        
        for obj_id, _, keywords, _ in found_objects:
            if any(word in keywords for word in negative_keywords):
                candidates.discard(obj_id)
        
        return candidates