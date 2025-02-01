import time
import numpy as np

# Benchmark Performance
class Benchmark:
    @staticmethod
    def run(query_processor, query, num_trials=5):
        times = []
        for _ in range(num_trials):
            start = time.time()
            query_processor.process_query(query)
            times.append(time.time() - start)
        print(f"Average Time: {np.mean(times)}")
        return np.mean(times)