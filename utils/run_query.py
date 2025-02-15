from index.teq_index import TEQIndex
from queries.power import POWERQueryProcessor
from utils.dataloader import load_dataset
import time
import numpy as np
from typing import List, Tuple
import os

def batch_process_data(data, batch_size: int = 100000) -> List[Tuple]:
    """Pre-process data into sorted batches for more efficient insertion"""
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

def query_runner(csv_name, save_dir="saved_index"):
    # Calculate bounds from data first to avoid reallocation
    dataset_path = "preprocessing/"+csv_name
    
    # Check if saved index exists
    if os.path.exists(save_dir) and os.path.isfile(os.path.join(save_dir, 'metadata.json')):
        print("Loading existing index...")
        teq = TEQIndex.load_index(save_dir)
    else:
        print("Building new index...")
        print("Loading Dataset")
        data = load_dataset(dataset_path)
        total_records = data.shape[0]
        print("Dataset Loaded total record:", total_records)

        # Calculate optimal bounds from data
        min_lat = data['Latitude'].min()
        max_lat = data['Latitude'].max()
        min_lon = data['Longitude'].min()
        max_lon = data['Longitude'].max()
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
        
        # Save the index
        teq.save_index(save_dir)

    # Run query
    power = POWERQueryProcessor(teq)
    query_start = time.time()
    
    results = power.process_query(
        location=(9.02579,7.47525),
        positive_keywords=["voice"],
        negative_keywords=["back"],
        k=5,
        lambda_factor=0.5
    )
    
    query_time = time.time() - query_start
    print(f"Query time: {query_time:.3f}s")
    print(f"Results: {results}")

    