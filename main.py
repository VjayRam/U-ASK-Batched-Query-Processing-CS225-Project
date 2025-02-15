from utils.run_query import query_runner, run_query_with_save, run_saved_queries



def main():
    run_query_with_save("split_data_40%.csv")
    # query_runner("split_data_20%.csv")
    sample_queries = [
        {
            'location': (9.02579, 7.47525),
            'positive_keywords': ['voice'],
            'negative_keywords': ['back'],
            'k': 5,
            'lambda_factor': 0.5
        },
        {
            'location': (9.12345, 7.54321),
            'positive_keywords': ['restaurant', 'food'],
            'negative_keywords': ['closed'],
            'k': 10,
            'lambda_factor': 0.7
        }
    ]
    
    
    results = run_saved_queries('saved_indexes/final', sample_queries)
        
        # Print detailed results if needed
    for result in results:
        print(f"\nQuery {result['query_id']} Results:")
        print(f"Parameters: {result['query_params']}")
        print(f"Time: {result['query_time']:.3f}s")
        print(f"Results: {result['results']}")
            
    



if __name__ == "__main__":
    main()