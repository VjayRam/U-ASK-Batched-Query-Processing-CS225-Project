import time
from benchmark.bench_perf import Benchmark
from index.teq_index import TEQIndex
from queries.power import POWERQueryProcessor
from utils.run_query import run_saved_queries
from analysis.result_analysis import ResultsAnalysis as Res
from benchmark.query_gen import QueryGenerator
from queries.batch_query import BatchPOWERQueryProcessor, create_batch_queries
from collections import defaultdict


def main():
    # run_build_index("split_data_100%.csv")
    # query_runner("split_data_100%.csv")
    # n = 1
    # n_pos = 2
    # n_neg = 2
    # k = [5]
    # lambda_factor = [0.5]
    # # loop over the indexes and run the queries for each index and store the average query time for each index in a dictionary
    # indexes = ['2M', '4M', '6M']
    # avg_query_times = {}
    # queries = []
    # qg = QueryGenerator()
    # for pos in range(1, n_pos+1):
    #     for neg in range(1, n_neg+1):
    #         for k_val in k:
    #             for lambda_val in lambda_factor:
    #                 queries.extend(qg.generate_queries(n, pos, neg, k_val, lambda_val))

    # for index in indexes:
    #     # generate n queries for each combination of n_positive keywords, n_negative keywords, k and lambda and store them in the queries list
    #     results, avg_query, _ = run_saved_queries(f'saved_indexes/{index}', queries)
    #     avg_query_times[index] = avg_query
    #     for result in results:
    #         print(f"\nQuery {result['query_id']} Results:")
    #         print(f"Parameters: {result['query_params']}")
    #         print(f"Time: {result['query_time']:.3f}s")
    #         print(f"Results: {result['results']}")

    # # plot the average query time for each index
    # Res.plot_line_results(avg_query_times, "Query Performance")  

    # teq_index = TEQIndex.load_index("saved_indexes/6M")
    
    # # Create batch processor
    # batch_processor = BatchPOWERQueryProcessor(teq_index, location_threshold=10.0)
    
    # # Define test locations and keywords (nearby locations grouped together)
    # locations = [
    #     # Group 1 - Downtown
    #     (9.02579, 7.47525),
    #     (9.02600, 7.47530),
    #     (9.02590, 7.47528),
    #     # Group 2 - Suburbs
    #     (9.15000, 7.35000),
    #     (9.15100, 7.35200),
    #     (9.15050, 7.35100),
    #     # Group 3 - Business District
    #     (9.08000, 7.42000),
    #     (9.08100, 7.42100),
    #     (9.08050, 7.42050),
    #     # Group 4 - Shopping Area
    #     (9.05000, 7.40000),
    #     (9.05100, 7.40100),
    #     (9.05050, 7.40050)
    # ]
    
    # keywords = [
    #     # Group 1 - Food & Dining
    #     ['restaurant', 'food'],
    #     ['cafe', 'coffee'],
    #     ['bar', 'drinks'],
    #     # Group 2 - Shopping
    #     ['mall', 'shopping'],
    #     ['market', 'retail'],
    #     ['store', 'clothes'],
    #     # Group 3 - Business
    #     ['office', 'business'],
    #     ['bank', 'finance'],
    #     ['company', 'corporate'],
    #     # Group 4 - Entertainment
    #     ['cinema', 'movies'],
    #     ['theater', 'shows'],
    #     ['park', 'recreation']
    # ]
    
    # # Create batch queries using helper function
    # queries = create_batch_queries(
    #     locations=locations,
    #     keywords=keywords,
    #     k=5,
    #     lambda_factor=0.5
    # )
    
    # # Process batch and print results
    # time_start = time.time()
    # results = batch_processor.process_batch_queries(queries)
    # time_end = time.time()
    
    # for query_id, query_results in results.items():
    #     print(f"\nResults for query {query_id}:")
    #     print(f"Location: {locations[query_id]}")
    #     print(f"Keywords: {keywords[query_id]}")
    #     print("Matches:")
    #     for score, obj_id, location, text in query_results:
    #         obj = teq_index.objects[obj_id]
    #         print(f"  Score: {-score:.3f}")
    #         print(f"  ID: {obj_id}")
    #         print(f"  Location: {location}")
    #         print(f"  Keywords: {list(obj['keywords'])}")
    #         print(f"  Text: {obj['full_text']}")
    #         print()
    # print(f"Time taken: {time_end - time_start:.3f}s")
    # print(f"Number of queries: {len(queries)}")
    # print(f"Number of results: {len(results)}")
    qg = QueryGenerator()
    queries = qg.generate_queries(100, 2, 2, 5, 0.5)
    indexes = ['2M', '4M', '6M','final']
    total_query_times_group = {}
    total_query_times_batch = {}
    total_query_times_combine= defaultdict(list)

    for ind in indexes:
        print(f"Running queries for index: {ind}")
        teq_index = TEQIndex.load_index(f"saved_indexes/{ind}")
        power = POWERQueryProcessor(teq_index)
        batch_processor = BatchPOWERQueryProcessor(teq_index, location_threshold=10.0)
        total_query_times_batch[ind] = Benchmark.run_batch_queries(batch_processor, queries)
        total_query_times_group[ind] = Benchmark.run_group_queries(power, queries)
        total_query_times_combine[ind].append(total_query_times_batch[ind])
        total_query_times_combine[ind].append(total_query_times_group[ind])
        print("************************************************")

    Res.plot_line_results(total_query_times_batch, "Batch Queries",y_label="Total Execution Time (s)")
    Res.plot_line_results(total_query_times_group, "Group Queries",y_label="Total Execution Time (s)")
    Res.plot_line_results(total_query_times_combine, "Combined Queries",y_label="Total Execution Time (s)")
if __name__ == "__main__":
    main()