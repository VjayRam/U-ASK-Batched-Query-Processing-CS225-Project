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
    def run(query_processor, query, num_trials=5):
        times = []
        for _ in range(num_trials):
            start = time.time()
            query_processor.process_query(query)
            times.append(time.time() - start)
        print(f"Average Time: {np.mean(times)}")
        return np.mean(times)