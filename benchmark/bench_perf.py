import time
import numpy as np

class Benchmark:
    """
    A class used to benchmark the performance of a query processor.

    Methods:
    run(query_processor, query, num_trials=5):
        Runs the benchmark by processing the query multiple times and 
        calculating the average time taken.
    """
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
    def run_batch_queries(query_processor, queries):
        time_start = time.time()
        results = query_processor.process_batch_queries(queries)
        time_end = time.time()
        print("--------------------------------")
        print("Batch Queries")
        print(f"Time taken: {time_end - time_start:.3f}s")
        print(f"Number of queries: {len(queries)}")
        print("--------------------------------")
        return time_end - time_start
