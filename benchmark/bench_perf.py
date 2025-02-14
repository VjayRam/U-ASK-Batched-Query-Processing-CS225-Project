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
    def run(query_processor, data,query, num_trials=5):
        times = []
        for _ in range(num_trials):
            start = time.time()
            results = query_processor.process_query(location=query["location"], positive_keywords=query["positive_keywords"], negative_keywords=query["negative_keywords"], k=query["k"], lambda_factor=query["lambda"])
            times.append(time.time() - start)
        print(f"Average Time: {np.mean(times)}")

        for result in results:
            print(data[result]==result)
        return np.mean(times)