import time
import numpy as np
from benchmark.query_gen import QueryGenerator
import os

class Benchmark:
    """
    A class used to benchmark the performance of a query processor.

    Methods:
    run(query_processor, query, num_trials=5):
        Runs the benchmark by processing the query multiple times and 
        calculating the average time taken.
    """
    @staticmethod
    def generate_experiment(n = 500, loc_ranges = [[(-90, 90), (-180, 180)]]):
        """_summary_

        Args:
            n (int, optional): _description_. Defaults to 500.
            loc_ranges (list, optional): _description_. Defaults to [[(-90, 90), (-180, 180)]].

        Returns:
            _type_: _description_
        """
        queries = []
        qg = QueryGenerator()
        
        for i in loc_ranges:
            queries += qg.generate_queries(n, 3, 2, 10, 0.5, i)
        print("Queries Generated!!")

        output_dir = "benchmark/data"
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, "generated_queries.txt")
        if os.path.exists(output_file):
            os.remove(output_file)
        with open(output_file, "a") as f:
            for query in queries:
                query_str = f"{query['location']}, {','.join(query['positive_keywords'])},{','.join(query['negative_keywords'])}, {query['k']}, {query['lambda_factor']}"
                f.write(query_str + "\n")
        print(f"Generated {n} queries and saved to {output_file}")
        return queries

    @staticmethod
    def run_single_query(query_processor,query, num_trials=5):
        """
        Runs a single query multiple times and calculates the average time taken.

        Args:
            query_processor (object): The query processor object that processes the query.
            query (dict): The query to be processed.
            num_trials (int, optional): The number of times the query should be run. Defaults to 5.

        Returns:
            float: The average time taken to process the query.
        """
        times = []
        for _ in range(num_trials):
            start = time.time()
            results = query_processor.process_query(location=query["location"], positive_keywords=query["positive_keywords"], negative_keywords=query["negative_keywords"], k=query["k"], lambda_factor=query["lambda_factor"])
            times.append(time.time() - start)
        print(f"Average Time: {np.mean(times)}")

        return np.mean(times) 
    
    @staticmethod
    def run_group_queries(query_processor, queries):
        """
        Runs a group of queries and calculates the total time taken.

        Args:
            query_processor (object): The query processor object that processes the queries.
            queries (list): A list of queries to be processed.

        Returns:
            float: The total time taken to process all queries.
        """
        times = []
        for query in queries:
            start = time.time()
            results = query_processor.process_query(location=query["location"], positive_keywords=query["positive_keywords"], negative_keywords=query["negative_keywords"], k=query["k"], lambda_factor=query["lambda_factor"])
            times.append(time.time() - start)
        print("--------------------------------")
        print("Group Queries")
        print(f"Average Time: {np.mean(times)}")
        print(f"Total Time: {np.sum(times)}")
        print(f"Number of queries: {len(queries)}")
        print(f"Results: {results}")
        print("--------------------------------")
        return np.sum(times)

    @staticmethod
    def run_batch_queries(query_processor, queries, cluster_size):
        """
        Runs a batch of queries in clusters and calculates the total time taken.

        Args:
            query_processor (object): The query processor object that processes the queries.
            queries (list): A list of queries to be processed.
            cluster_size (int): The size of each cluster of queries to be processed together.

        Returns:
            float: The total time taken to process all queries.
        """
        n = len(queries)
        time_start = time.time()
        results = query_processor.process_batch_queries(queries, cluster_size)
        time_end = time.time()
        print("--------------------------------")
        print("Batch Queries")
        print(f"Average Time: {(time_end - time_start)/n}")
        print(f"Total Time: {time_end - time_start:.3f}s")
        print(f"Number of queries: {len(queries)}")
        print(f"Results: {results}")
        print("--------------------------------")
        return time_end - time_start
    
    @staticmethod
    def variable_cluster_test(query_processor, queries, cluster_sizes=[10, 20, 40, 60, 80, 100]):
        """
        Tests the performance of batch query processing with different cluster sizes.

        Args:
            query_processor (object): The query processor object that processes the queries.
            queries (list): A list of queries to be processed.
            cluster_sizes (list, optional): A list of cluster sizes to test. Defaults to [10, 20, 40, 60, 80, 100].

        Returns:
            list: A list of total times taken to process the queries for each cluster size.
        """
        n = len(queries)
        res = []
        print("--------------------------------")
        print("Batch Queries for variable cluster sizes")
        for i in cluster_sizes:
            time_start = time.time()
            results = query_processor.process_batch_queries(queries, i)
            time_end = time.time()
            print("--------------------------------")
            print(f"Cluster Size: {i}")
            print(f"Average Time: {(time_end - time_start)/n}")
            print(f"Total Time: {time_end - time_start:.3f}s")
            print(f"Number of queries: {len(queries)}")
            print(f"Results: {results}")
            print("--------------------------------")
            res.append(time_end-time_start)

        return res
