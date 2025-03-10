import time
from benchmark.bench_perf import Benchmark
from index.teq_index import TEQIndex
from queries.power import POWERQueryProcessor
from utils.run_query import run_saved_queries
from analysis.result_analysis import ResultsAnalysis as Res
from benchmark.query_gen import QueryGenerator
from queries.batch_query import BatchPOWERQueryProcessor, create_batch_queries
from collections import defaultdict
import os



def main():

    # To build index load the data and run the build index function
    # run_build_index("split_data_100%.csv")
    
    
    # teq_index = TEQIndex.load_index("saved_indexes/6M")
    
    # # Create batch processor
    # batch_processor = BatchPOWERQueryProcessor(teq_index, location_threshold=10.0)
    
    queries = Benchmark.generate_experiment(10)
    cluster_size = 20
    cluster_sizes = [10, 20, 50, 100]
    
    indexes = ['final']
    total_query_times_group = {}
    total_query_times_batch = {}
    total_query_times_combine= defaultdict(list)

    for ind in indexes:
        print(f"Running queries for index: {ind}")
        teq_index = TEQIndex.load_index(f"saved_indexes/{ind}")
        power = POWERQueryProcessor(teq_index)
        batch_processor = BatchPOWERQueryProcessor(teq_index, location_threshold=10.0)
        total_query_times_batch[ind] = Benchmark.run_batch_queries(batch_processor, queries, cluster_size)
        total_query_times_group[ind] = Benchmark.run_group_queries(power, queries)
        total_query_times_combine[ind].append(total_query_times_batch[ind])
        total_query_times_combine[ind].append(total_query_times_group[ind])
        query_times_for_cluster = Benchmark.variable_cluster_test(batch_processor, queries, cluster_sizes)
        print("************************************************")

    # Res.plot_line_results(total_query_times_batch, "Batch Queries",y_label="Total Execution Time (s)")
    # Res.plot_line_results(total_query_times_group, "Group Queries",y_label="Total Execution Time (s)")
    # Res.plot_line_results(total_query_times_combine, "Combined Queries",y_label="Total Execution Time (s)")
    # Res.plot_cluster_results(query_times_for_cluster, cluster_sizes)

if __name__ == "__main__":
    main()