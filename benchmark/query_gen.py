import random


class QueryGenerator:
    """
    This class provides methods to generate spatial computing queries.

    Methods:
    - generate_queries(n, location_range, keyword_range, k_range, lambda_range): Generates n random queries with the given parameters.
    """
    def __init__(self, lat_range=(-90, 90), lon_range=(-180, 180), keyword_range=(1, 5), k_range=(1, 10000), lambda_range=(0, 1)):
        self.lat_range = lat_range
        self.lon_range = lon_range
        self.keyword_range = keyword_range
        self.k_range = k_range
        self.lambda_range = lambda_range
        self.keywords = ['restaurant', 'food', 'voice', 'closed', 'back', 'open', 'park', 'hotel', 'shop', 'store', 'market', 'school', 'hospital', 'bank', 'cafe', 'bar', 'club', 'gym', 'library', 'theater', 'cinema', 'museum', 'parking', 'zoo', 'garden', 'pool', 'beach', 'lake', 'river', 'mountain', 'forest', 'road', 'bridge', 'building', 'house', 'apartment', 'office', 'factory', 'warehouse', 'hospital', 'pharmacy', 'clinic', 'doctor', 'nurse', 'police', 'fire', 'ambulance', 'bus', 'train', 'subway', 'taxi', 'car', 'bike', 'motorcycle', 'plane', 'boat', 'ship', 'truck', 'helicopter', 'rocket', 'satellite', 'computer', 'phone', 'tablet', 'tv', 'radio', 'internet', 'wifi', 'bluetooth', 'gps', 'camera', 'music', 'video', 'game', 'social', 'email', 'message', 'chat', 'call', 'video', 'photo', 'file', 'document', 'app', 'software', 'hardware', 'network', 'server', 'cloud', 'database', 'programming', 'security', 'privacy', 'encryption', 'password', 'username', 'login', 'logout', 'register', 'profile', 'setting', 'help', 'support', 'faq', 'terms', 'policy', 'contact', 'about', 'news', 'blog', 'article', 'video', 'photo', 'audio', 'podcast', 'live', 'event', 'meeting', 'conference', 'seminar', 'workshop', 'training', 'course', 'class', 'lesson', 'lecture', 'presentation', 'talk', 'discussion', 'conversation', 'interview', 'panel', 'debate', 'forum', 'survey', 'poll', 'quiz', 'test', 'exam', 'assignment', 'home']

    def generate_queries(self, n, n_pos, n_neg, k, lambda_factor, loc=[(-90, 90), (-180, 180)]):
        lat_range = loc[0]
        lon_range = loc[1]
        queries = []
        # select random 20 keywords from the list of keywords
        for _ in range(n):
            location = (random.uniform(*lat_range), random.uniform(*lon_range))
            positive_keywords = random.sample(self.keywords, n_pos)
            negative_keywords = random.sample(self.keywords, n_neg)
            queries.append({
                'location': location,
                'positive_keywords': positive_keywords,
                'negative_keywords': negative_keywords,
                'k': k,
                'lambda_factor': lambda_factor
            })
        return queries
    

"""def main():
    # Generate queries and save them to a file
    query_generator = QueryGenerator()
    n = 125  # Number of queries to generate
    n_pos = 3  # Number of positive keywords per query
    n_neg = 2  # Number of negative keywords per query
    k = 10  # Number of results to return
    lambda_factor = 0.5  # Lambda factor for ranking
    
    queries = query_generator.generate_queries(n, n_pos, n_neg, k, lambda_factor)
    
    # Save queries to a file
    import os
    
    output_dir = "benchmark/data"
    os.makedirs(output_dir, exist_ok=True)
    
    output_file = os.path.join(output_dir, "generated_queries.txt")
    with open(output_file, "w") as f:
        for query in queries:
            query_str = f"{query['location']}, {','.join(query['positive_keywords'])},{','.join(query['negative_keywords'])}, {query['k']}, {query['lambda_factor']}"
            f.write(query_str + "\n")
    
    print(f"Generated {n} queries and saved to {output_file}")

if __name__ == "__main__":
    main()
"""