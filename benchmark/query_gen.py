import random


class QueryGenerator:
    """
    QueryGenerator class generates spatial queries with random locations and keywords.
    
    Attributes:
        lat_range (tuple): Range of latitudes for generating random locations.
        lon_range (tuple): Range of longitudes for generating random locations.
        keyword_range (tuple): Range of number of keywords to be included in the queries.
        k_range (tuple): Range of 'k' values for the queries.
        lambda_range (tuple): Range of 'lambda' values for the queries.
        keywords (list): List of possible keywords to be included in the queries.
    """
    def __init__(self, lat_range=(-90, 90), lon_range=(-180, 180), keyword_range=(1, 5), k_range=(1, 10000), lambda_range=(0, 1)):
        self.lat_range = lat_range
        self.lon_range = lon_range
        self.keyword_range = keyword_range
        self.k_range = k_range
        self.lambda_range = lambda_range
        self.keywords = ['restaurant', 'food', 'voice', 'closed', 'back', 'open', 'park', 'hotel', 'shop', 'store', 'market', 'school', 'hospital', 'bank', 'cafe', 'bar', 'club', 'gym', 'library', 'theater', 'cinema', 'museum', 'parking', 'zoo', 'garden', 'pool', 'beach', 'lake', 'river', 'mountain', 'forest', 'road', 'bridge', 'building', 'house', 'apartment', 'office', 'factory', 'warehouse', 'hospital', 'pharmacy', 'clinic', 'doctor', 'nurse', 'police', 'fire', 'ambulance', 'bus', 'train', 'subway', 'taxi', 'car', 'bike', 'motorcycle', 'plane', 'boat', 'ship', 'truck', 'helicopter', 'rocket', 'satellite', 'computer', 'phone', 'tablet', 'tv', 'radio', 'internet', 'wifi', 'bluetooth', 'gps', 'camera', 'music', 'video', 'game', 'social', 'email', 'message', 'chat', 'call', 'video', 'photo', 'file', 'document', 'app', 'software', 'hardware', 'network', 'server', 'cloud', 'database', 'programming', 'security', 'privacy', 'encryption', 'password', 'username', 'login', 'logout', 'register', 'profile', 'setting', 'help', 'support', 'faq', 'terms', 'policy', 'contact', 'about', 'news', 'blog', 'article', 'video', 'photo', 'audio', 'podcast', 'live', 'event', 'meeting', 'conference', 'seminar', 'workshop', 'training', 'course', 'class', 'lesson', 'lecture', 'presentation', 'talk', 'discussion', 'conversation', 'interview', 'panel', 'debate', 'forum', 'survey', 'poll', 'quiz', 'test', 'exam', 'assignment', 'home']

    def generate_queries(self, n, n_pos, n_neg, k, lambda_factor, loc=[(-90, 90), (-180, 180)]):
        """
        Generates a list of spatial queries with random locations and keywords.

        Args:
            n (int): Number of queries to generate.
            n_pos (int): Number of positive keywords per query.
            n_neg (int): Number of negative keywords per query.
            k (int): The 'k' value for the queries.
            lambda_factor (float): The 'lambda' value for the queries.
            loc (list, optional): List containing the latitude and longitude ranges. Defaults to [(-90, 90), (-180, 180)].

        Returns:
            list: A list of dictionaries, each representing a query with location, positive keywords, negative keywords, 'k' value, and 'lambda' value.
        """
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
    

