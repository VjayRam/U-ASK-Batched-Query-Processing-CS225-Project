from index.teq_index import TEQIndex
from queries.power import POWERQueryProcessor
from utils.dataloader import load_dataset
import time
import numpy as np
from typing import List, Tuple
import os

def batch_process_data(data, batch_size: int = 100000) -> List[Tuple]:
    """_summary_
    Process data into batches for efficient indexing.
    
    This function takes a pandas DataFrame containing spatial-textual data and converts it into batches
    of tuples for more efficient processing. Each tuple contains:
    - ObjectID: Unique identifier for the record
    - Location: (Latitude, Longitude) coordinates
    - Keywords: Associated keywords/tags
    - FullText: Complete text description
    
    The records are sorted by location coordinates to optimize spatial indexing performance.

    Args:
        data (_type_): _description_
        batch_size (int, optional): _description_. Defaults to 100000.

    Returns:
        List[Tuple]: _description_
    """
    # Convert data to list of tuples for faster processing
    records = []
    for _, row in data.iterrows():
        records.append((
            row['ObjectID'],
            (row['Latitude'], row['Longitude']),
            row['Keywords'],
            row['FullText']
        ))
    
    # Sort records by location for more efficient spatial indexing
    records.sort(key=lambda x: (x[1][0], x[1][1]))
    
    # Split into batches
    return [records[i:i + batch_size] for i in range(0, len(records), batch_size)]

def query_runner_without_save(csv_name,location:Tuple[float,float],positive_keywords:List[str],negative_keywords:List[str],k:int,lambda_factor:float):
    """
    Run a query without saving the index
    
    This function loads a dataset from a CSV file, processes it into batches for efficient indexing,
    and then runs a query on the index without saving it. It returns the results of the query.
    
    Args:
        csv_name: Name of the CSV file to process
        location: Tuple containing latitude and longitude
        positive_keywords: List of positive keywords to match
        negative_keywords: List of negative keywords to exclude
        k: Number of results to return
        lambda_factor: Weight between spatial and textual relevance
    """
    # Calculate bounds from data first to avoid reallocation
    dataset_path = "preprocessing/"+csv_name
    
   
    print("Building new index...")
    print("Loading Dataset")
    data = load_dataset(dataset_path)
    total_records = data.shape[0]
    print("Dataset Loaded total record:", total_records)

    # Calculate optimal bounds from data
    min_lat = data['Latitude'].min()
    max_lat = data['Latitude'].max()
    min_lon = data['Longitude'].min()
    max_lon = data['Longitude'].min()
    bounds = (min_lat, min_lon, max_lat, max_lon)
        
    # Initialize index with calculated bounds
    teq = TEQIndex(bounds)
        
    # Process data in batches
    batch_size = 100000  # Adjust based on available memory
    start_time = time.time()
        
    batches = batch_process_data(data, batch_size)
    total_batches = len(batches)
        
    print(f"Processing {total_batches} batches of {batch_size} records each")
        
    for i, batch in enumerate(batches, 1):
        batch_start = time.time()
            
            # Insert batch
        for obj_id, location, keywords, full_text in batch:
            teq.add_object(obj_id, location, keywords, full_text)
            
        batch_time = time.time() - batch_start
        records_per_sec = len(batch) / batch_time
            
        print(f"Batch {i}/{total_batches} completed in {batch_time:.2f}s "
                  f"({records_per_sec:.0f} records/sec)")
        
    total_index_time = time.time() - start_time
    print(f"Total index build time: {total_index_time:.2f}s "
    f"({total_records/total_index_time:.0f} records/sec average)")
        
    # Run query
    power = POWERQueryProcessor(teq)
    query_start = time.time()
    
    print(f"Running query with parameters: location={location}, positive_keywords={positive_keywords}, negative_keywords={negative_keywords}, k={k}, lambda_factor={lambda_factor}")
    try:
        results = power.process_query(
            location=(location[0], location[1]),
            positive_keywords=positive_keywords,
            negative_keywords=negative_keywords,
            k=k,
                lambda_factor=lambda_factor
            )
        query_time = time.time() - query_start
        print(f"Query time: {query_time:.3f}s")
        print(f"Results: {results}")
    except Exception as e:
        print(f"Error: {e}")
        print("Please check the query parameters")
        return None
    
    

def run_saved_queries(save_dir: str, queries: List[dict]) -> List[dict]:
    """
    Load a saved index and run multiple queries against it
    
    Args:
        save_dir: Directory containing the saved index
        queries: List of query dictionaries, each containing:
                {
                    'location': (lat, lon),
                    'positive_keywords': list of keywords to match,
                    'negative_keywords': list of keywords to exclude,
                    'k': number of results to return,
                    'lambda_factor': weight between spatial and textual relevance
                }
    
    Returns:
        List of dictionaries containing query results and timing information
    """
    if not os.path.exists(save_dir) or not os.path.isfile(os.path.join(save_dir, 'metadata.json')):
        raise FileNotFoundError(f"No saved index found in {save_dir}")
    
    print(f"Loading index from {save_dir}...")
    load_start = time.time()
    teq = TEQIndex.load_index(save_dir)
    load_time = time.time() - load_start
    print(f"Index loaded in {load_time:.2f}s")
    
    power = POWERQueryProcessor(teq)
    results = []

    for i, query in enumerate(queries, 1):
        print(f"\nExecuting query {i}/{len(queries)}")
        query_start = time.time()
        
        query_results = power.process_query(
            location=query['location'],
            positive_keywords=query['positive_keywords'],
            negative_keywords=query['negative_keywords'],
            k=query['k'],
            lambda_factor=query['lambda_factor']
        )
        
        query_time = time.time() - query_start
        
        result = {
            'query_id': i,
            'query_params': query,
            'results': query_results,
            'query_time': query_time
        }
        results.append(result)
        
        print(f"Query {i} completed in {query_time:.3f}s")
        print(f"Found {len(query_results)} results")
    
    # Print summary
    total_query_time = sum(r['query_time'] for r in results)
    avg_query_time = total_query_time / len(queries)
    print(f"\nQuery Summary:")
    print(f"Total queries executed: {len(queries)}")
    print(f"Average query time: {avg_query_time:.3f}s")
    print(f"Total query time: {total_query_time:.3f}s")
    
    return results, total_query_time, avg_query_time

def run_build_index(csv_name, save_dir="saved_indexes", force_rebuild=True):
    """
    Build or load index and save it periodically
    
    Args:
        csv_name: Name of the CSV file to process
        save_dir: Main directory for all saved indexes
        force_rebuild: If True, rebuild index even if it exists
    """
    # Check and clean directory if it exists
    if os.path.exists(save_dir):
        print(f"Removing existing index directory: {save_dir}")
        import shutil
        shutil.rmtree(save_dir)
    
    # Create fresh directory
    os.makedirs(save_dir)
    print(f"Created new index directory: {save_dir}")
    
    # Load and process dataset
    dataset_path = "preprocessing/" + csv_name
    print("Loading Dataset...")
    data = load_dataset(dataset_path)
    total_records = data.shape[0]
    print(f"Dataset Loaded total records: {total_records:,}")

    # Calculate bounds from data
    min_lat = data['Latitude'].min()
    max_lat = data['Latitude'].max()
    min_lon = data['Longitude'].min()
    max_lon = data['Longitude'].max()
    bounds = (min_lat, min_lon, max_lat, max_lon)
    
    # Initialize index
    teq = TEQIndex(bounds)
    
    # Process data in batches
    batch_size = 200000  # 200K records per batch
    start_time = time.time()
    
    batches = batch_process_data(data, batch_size)
    total_batches = len(batches)
    
    print(f"Processing {total_batches} batches of {batch_size:,} records each")
    
    for i, batch in enumerate(batches, 1):
        batch_start = time.time()
        
        # Insert batch
        for obj_id, location, keywords, full_text in batch:
            teq.add_object(obj_id, location, keywords, full_text)
        
        batch_time = time.time() - batch_start
        records_per_sec = len(batch) / batch_time
        
        print(f"Batch {i}/{total_batches} completed in {batch_time:.2f}s "
              f"({records_per_sec:,.0f} records/sec)")
        
        # Save milestone index every 2 million records
        current_total = i * batch_size
        if current_total % 2000000 == 0 or current_total >= total_records:
            milestone = (current_total // 2000000) * 2
            milestone_dir = os.path.join(save_dir, f"{milestone}M")
            os.makedirs(milestone_dir, exist_ok=True)
            
            teq.save_index(milestone_dir)
            print(f"\nSaved {milestone}M milestone index to {milestone_dir}")
    
    milestone_dir = os.path.join(save_dir, "final")
    os.makedirs(milestone_dir, exist_ok=True)
    teq.save_index(milestone_dir)
    print(f"\nSaved {milestone}M milestone index to {milestone_dir}")
    
           
    total_index_time = time.time() - start_time
    print(f"\nIndexing Summary:")
    print(f"Total index build time: {total_index_time:.2f}s")
    print(f"Average speed: {total_records/total_index_time:,.0f} records/sec")
    print(f"Total records processed: {total_records:,}")
    
    return teq

