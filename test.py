from analysis.result_analysis import ResultsAnalysis
from benchmark.bench_perf import Benchmark
from index.teq_index import TEQIndex
from queries.power import POWERQueryProcessor
from utils.dataloader import load_dataset

# class QuadtreeNode:
#     def __init__(self, bounds, capacity=4):
#         self.bounds = bounds  # (x_min, y_min, x_max, y_max)
#         self.capacity = capacity
#         self.objects = []  # Stores (obj_id, location, keywords, full_text)
#         self.children = None
    
#     def subdivide(self):
#         x_min, y_min, x_max, y_max = self.bounds
        
        
#         mid_x = (x_min + x_max) / 2
#         mid_y = (y_min + y_max) / 2

#         self.children = [
#             QuadtreeNode((x_min, y_min, mid_x, mid_y), self.capacity),  # Bottom-left
#             QuadtreeNode((mid_x, y_min, x_max, mid_y), self.capacity),  # Bottom-right
#             QuadtreeNode((x_min, mid_y, mid_x, y_max), self.capacity),  # Top-left
#             QuadtreeNode((mid_x, mid_y, x_max, y_max), self.capacity)   # Top-right
#         ]


    
#     def insert(self, obj_id, location, keywords, full_text):
#     # Check if the object is within the bounds of this node
#         if not (self.bounds[0] <= location[0] <= self.bounds[2] and self.bounds[1] <= location[1] <= self.bounds[3]):
#             return False  # Object is outside bounds
        
#         if len(self.objects) < self.capacity and self.children is None:
#             self.objects.append((obj_id, location, keywords, full_text))
#             return True

#         if self.children is None:
#             self.subdivide()
        
#         for child in self.children:
#             if child.insert(obj_id, location, keywords, full_text):
#                 return True

#         return False

    
#     def query_range(self, bounds, found_objects):
#         x_min, y_min, x_max, y_max = self.bounds
#         q_x_min, q_y_min, q_x_max, q_y_max = bounds
        
#         if q_x_max < x_min or q_x_min > x_max or q_y_max < y_min or q_y_min > y_max:
#             return  # No overlap
        
#         for obj in self.objects:
#             found_objects.append(obj)
        
#         if self.children is not None:
#             for child in self.children:
#                 child.query_range(bounds, found_objects)

# class TEQIndex:
#     def __init__(self, bounds):
#         self.spatial_index = QuadtreeNode(bounds)
#         self.objects = {}  # Stores full object details

#     def add_object(self, obj_id, location, keywords, full_text):
#         self.objects[obj_id] = {'location': location, 'keywords': keywords, 'full_text': full_text}
#         self.spatial_index.insert(obj_id, location, keywords, full_text)
    
#     def get_candidates(self, location, positive_keywords, negative_keywords, search_radius=10):
#         x, y = location
#         bounds = (x - search_radius, y - search_radius, x + search_radius, y + search_radius)
#         found_objects = []
#         self.spatial_index.query_range(bounds, found_objects)
        
#         candidates = {obj_id for obj_id, _, keywords, _ in found_objects if any(word in keywords for word in positive_keywords)}
        
#         for obj_id, _, keywords, _ in found_objects:
#             if any(word in keywords for word in negative_keywords):
#                 candidates.discard(obj_id)
        
#         return candidates

# class POWERQueryProcessor:
#     def __init__(self, teq_index):
#         self.teq_index = teq_index
    
#     def compute_distance(self, loc1, loc2):
#         return sqrt((loc1[0] - loc2[0]) ** 2 + (loc1[1] - loc2[1]) ** 2)
    
#     def count_keyword_matches(self, keywords, positive_keywords):
#         return sum(1 for word in positive_keywords if word in keywords)
    
#     def process_query(self, location, positive_keywords, negative_keywords, k, lambda_factor=0.5):
#         candidates = self.teq_index.get_candidates(location, positive_keywords, negative_keywords)
        
#         heap = []
#         for obj_id in candidates:
#             obj = self.teq_index.objects[obj_id]
#             spatial_score = 1 - self.compute_distance(location, obj['location']) / 100
#             textual_score = self.count_keyword_matches(obj['keywords'], positive_keywords)
#             score = lambda_factor * spatial_score + (1 - lambda_factor) * textual_score
#             heapq.heappush(heap, (-score, obj_id))
        
#         return [heapq.heappop(heap)[1] for _ in range(min(k, len(heap)))]

# Example Usage
bounds = (0, 0, 200, 200)  # Define Quadtree boundary
teq = TEQIndex(bounds)
dataset_path = "preprocessing/dataset.csv"
print("Loading Dataset")
data = load_dataset(dataset_path) 
print("Dataset Loaded", data.shape)
count = 0
for _, row in data.iterrows():
    count += 1
    teq.add_object(row['ObjectID'], (row['Latitude'], row['Longitude']), row['Keywords'],row['FullText'])

power = POWERQueryProcessor(teq)
tkqn_query = {"location": (24.80369295, 46.62080736), "positive_keywords": ["dress"], "negative_keywords": ["fabrics"], "lambda": 0.5, "k": 5}

results = {  "TKQN": Benchmark.run(power, tkqn_query)}
ResultsAnalysis.plot_results(results)
