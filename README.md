# CS225 W25 - Spatial Computing Project

U-ASK is a unified indexing and query processing system for kNN spatial-keyword queries that supports negative keyword predicates, as presented in ACM SIGSPATIAL 2022. This project extends U-ASK to support additional types of spatial-keyword queries. The U-ASK paper is cited below:

> Liu, Y., & Magdy, A. (2022). U-ASK: a unified architecture for kNN spatial-keyword queries supporting negative keyword predicates. In Proceedings of the 30th International Conference on Advances in Geographic Information Systems (SIGSPATIAL '22). Article 40, 1–11.

## Project Overview

This project implements a spatial computing system that efficiently processes geospatial data and handles spatial queries. It focuses on optimizing the retrieval of location-based information through advanced spatial indexing and query processing techniques. The system includes:

1. A spatial index using quadtree data structure for efficient spatial queries
2. Text and keyword-based filtering for precise information retrieval
3. Batch query processing with clustering optimization
4. Benchmarking tools to measure and compare performance

## Project Structure

### `/models`

Contains the core data structures for spatial indexing:

- `quadtree.py`: Implementation of a quadtree spatial index structure optimized for geospatial data

### `/index`

Includes the indexing implementation:

- `teq_index.py`: Text-Enhanced Quadtree Index that combines spatial indexing with text-based search capabilities

### `/queries`

Contains query processing implementations:

- `power.py`: POint-based With Enhanced Retrieval (POWER) query processor
- `batch_query.py`: Optimized batch query processor that handles multiple queries efficiently using clustering techniques

### `/preprocessing`

Data preprocessing tools:

- `data_preprocessor.py`: Tools for loading, cleaning, and pre-processing spatial datasets

### `/benchmark`

Performance evaluation tools:

- `bench_perf.py`: Benchmarking utilities for measuring query performance
- `query_gen.py`: Query generation tools for creating test queries

### `/analysis`

Result analysis tools:

- `result_analysis.py`: Visualization and analysis tools for benchmark results

## Setup and Installation

### Prerequisites

- Python 3.9 or newer
- Required Python packages: numpy, scipy, pandas, matplotlib

### Installation Steps

1. Clone the repository or extract the project files

2. Create and activate a virtual environment:

   ```
   python -m venv env
   source env/bin/activate  # On Windows, use: env\Scripts\activate
   ```

3. Install required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Running the Project

### Data Preparation

1. Prepare your spatial dataset in the expected format or use the provided data preprocessing tools:

   ```
   python preprocessing/data_preprocessor.py
   ```

2. Place your dataset in the project directory or specify the path in the code.

### Building the Spatial Index

1. To build the spatial index, modify the `main.py` file to uncomment the index building function:

   ```python
   # Uncomment this line to build the index
   run_build_index("your_dataset.csv")
   ```

2. Run the main script:
   ```
   python main.py
   ```

### Running Queries

1. For individual queries, you can use the POWERQueryProcessor:

   ```python
   from index.teq_index import TEQIndex
   from queries.power import POWERQueryProcessor

   # Load saved index
   teq_index = TEQIndex.load_index("saved_indexes/your_index_name")

   # Create query processor
   power = POWERQueryProcessor(teq_index)

   # Run a query
   results = power.process_query(
        location=(latitude, longitude),
        positive_keywords=["keyword1", "keyword2"],
        negative_keywords=["exclude1"],
        k=10,
        lambda_factor=0.5
   )
   ```

2. For batch queries, use the BatchPOWERQueryProcessor:

   ```python
   from queries.batch_query import BatchPOWERQueryProcessor, create_batch_queries

   # Create batch processor
   batch_processor = BatchPOWERQueryProcessor(teq_index, location_threshold=10.0)

   # Create batch queries
   queries = create_batch_queries(
        locations=[(lat1, lon1), (lat2, lon2), ...],
        keywords=[["kw1", "kw2"], ["kw3", "kw4"], ...],
        k=10,
        lambda_factor=0.5
   )

   # Process batch
   results = batch_processor.process_batch_queries(queries, cluster_size=20)
   ```

### Running Benchmarks

1. Generate queries for benchmarking:

   ```python
   from benchmark.query_gen import QueryGenerator

   qg = QueryGenerator()
   queries = qg.generate_queries(n=100, n_pos=3, n_neg=2, k=10, lambda_factor=0.5)
   ```

2. Run benchmarks:

   ```python
   from benchmark.bench_perf import Benchmark

   # For individual query processing
   group_time = Benchmark.run_group_queries(power, queries)

   # For batch query processing
   batch_time = Benchmark.run_batch_queries(batch_processor, queries, cluster_size=20)

   # Test with different cluster sizes
   cluster_results = Benchmark.variable_cluster_test(
        batch_processor,
        queries,
        cluster_sizes=[10, 20, 50, 100]
   )
   ```

3. Visualize results:

   ```python
   from analysis.result_analysis import ResultsAnalysis

   # Plot comparison between group and batch processing
   ResultsAnalysis.plot_results(
        {"Group": group_time, "Batch": batch_time},
        title="Query Processing Performance"
   )

   # Plot cluster size impact
   ResultsAnalysis.plot_cluster_results(
        cluster_results,
        [10, 20, 50, 100],
        title="Impact of Cluster Size on Performance"
   )
   ```

## Implementation Details

### Spatial Indexing

The project uses a quadtree-based spatial index that recursively divides space into four quadrants to efficiently organize spatial data. This allows for quick retrieval of objects within a specific area.

### Query Processing

- **POWER Query**: Combines spatial proximity with keyword relevance to provide ranked results.
- **Batch Processing**: Optimizes multiple queries by grouping similar queries based on location and keywords to minimize redundant computations.

### Performance Optimization

The implementation includes several optimizations:

- Dynamic clustering of queries to balance processing efficiency and result quality
- Memory-efficient data structures with object caching
- Buffered batch processing to reduce overhead
- Early termination strategies for query processing

## Additional Notes

- For large datasets, increase the buffer size in `teq_index.py` to improve index building performance.
- Adjust cluster sizes in batch processing based on your specific use case to find the optimal balance between performance and result quality.
- The system supports saving and loading indexes to avoid rebuilding for large datasets.

## Team Members

- [Vijay Ram Enaganti](https://github.com/VjayRam)
- [Manoj Manjunatha](https://github.com/manu042k)
- [Anirudh Nittur Venkatesh](https://github.com/aninv18)
