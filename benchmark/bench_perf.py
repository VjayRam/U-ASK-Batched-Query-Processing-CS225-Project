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
        queries = []
        qg = QueryGenerator()
        
        for i in loc_ranges:
            queries += qg.generate_queries(n, 3, 2, 10, 0.5, i)
        print("Queries Generated!!")

        output_dir = "benchmark/data"
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, "generated_queries.txt")
        with open(output_file, "a") as f:
            for query in queries:
                query_str = f"{query['location']}, {','.join(query['positive_keywords'])},{','.join(query['negative_keywords'])}, {query['k']}, {query['lambda_factor']}"
                f.write(query_str + "\n")
        print(f"Generated {n} queries and saved to {output_file}")
        return queries

    @staticmethod
    def run_single_query(query_processor,query, num_trials=5):
        times = []
        for _ in range(num_trials):
            start = time.time()
            results = query_processor.process_query(location=query["location"], positive_keywords=query["positive_keywords"], negative_keywords=query["negative_keywords"], k=query["k"], lambda_factor=query["lambda_factor"])
            times.append(time.time() - start)
        print(f"Average Time: {np.mean(times)}")

        return np.mean(times) 
    
    @staticmethod
    def run_group_queries(query_processor, queries):
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
        print("--------------------------------")
        return np.sum(times)

    @staticmethod
    def run_batch_queries(query_processor, queries, cluster_size):
        n = len(queries)
        time_start = time.time()
        results = query_processor.process_batch_queries(queries, cluster_size)
        time_end = time.time()
        print("--------------------------------")
        print("Batch Queries")
        print(f"Average Time: {(time_end - time_start)/n}")
        print(f"Total Time: {time_end - time_start:.3f}s")
        print(f"Number of queries: {len(queries)}")
        print("--------------------------------")
        return time_end - time_start
