from utils.dataloader import load_dataset
from index.teq_index import TEQIndex
from queries.power import POWER
from queries.power_bf import POWER_BF
from queries.range_queries import RangeQuery
from benchmark.bench_perf import Benchmark
from analysis.result_analysis import ResultsAnalysis
import time
import numpy as np


def main():
    # start timer 
    start = time.time()
    dataset_path = "data/dataset.csv"
    print("Loading Dataset")
    data = load_dataset(dataset_path)
    
    teq = TEQIndex()
    teq.build_index(data)
    
    tkqn_query = {"location": (24.80369295, 46.62080736), "positive_keywords": ["dress"], "negative_keywords": ["fabrics"], "lambda": 0.5, "k": 5}
    bkqn_query = {"location": (28.42029633, -81.58333817), "and_keywords": ["talk"], "or_keywords": ["shit"], "negative_keywords": ["fucked"], "k": 3}
    range_query = {"location": (20.0, -65.0), "radius": 10, "negative_keywords": ["age"]}
    
    power = POWER(teq)
    power_bf = POWER_BF(teq)
    range_q = RangeQuery(teq)
    
    results = {
        "TKQN": Benchmark.run(power, tkqn_query),
        "BKQN": Benchmark.run(power_bf, bkqn_query),
        "RangeQuery": Benchmark.run(range_q, range_query)
    }
    
    ResultsAnalysis.plot_results(results)
    print(f"Total Time: {time.time() - start}")
    
if __name__ == "__main__":
    main()