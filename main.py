from utils.run_query import run_saved_queries
from analysis.result_analysis import ResultsAnalysis as Res
from benchmark.query_gen import QueryGenerator



def main():
    # run_build_index("split_data_100%.csv")
    # query_runner("split_data_100%.csv")

    #TODO: create a benchmarkar for the query performance base on graphs reqired in the report
    n = 1
    n_pos = 2
    n_neg = 2
    k = [5]
    lambda_factor = [0.5]
    # loop over the indexes and run the queries for each index and store the average query time for each index in a dictionary
    indexes = ['2M', '4M', '6M']
    avg_query_times = {}
    queries = []
    qg = QueryGenerator()
    for pos in range(1, n_pos+1):
        for neg in range(1, n_neg+1):
            for k_val in k:
                for lambda_val in lambda_factor:
                    queries.extend(qg.generate_queries(n, pos, neg, k_val, lambda_val))

    for index in indexes:
        # generate n queries for each combination of n_positive keywords, n_negative keywords, k and lambda and store them in the queries list
        results, avg_query, _ = run_saved_queries(f'saved_indexes/{index}', queries)
        avg_query_times[index] = avg_query
        for result in results:
            print(f"\nQuery {result['query_id']} Results:")
            print(f"Parameters: {result['query_params']}")
            print(f"Time: {result['query_time']:.3f}s")
            print(f"Results: {result['results']}")

    # plot the average query time for each index
    Res.plot_line_results(avg_query_times, "Query Performance")    

if __name__ == "__main__":
    main()