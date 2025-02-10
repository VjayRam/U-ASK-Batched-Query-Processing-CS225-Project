import pandas as pd
import time

def load_dataset(csv_path):
    """
    Load a dataset from a CSV file, process 'Keywords' and 'Weights' columns.

    Args:
        csv_path (str): The file path to the CSV file.

    Returns:
        pandas.DataFrame: The loaded and processed DataFrame.

    The function reads a CSV file into a pandas DataFrame, processes the 'Keywords' 
    and 'Weights' columns by evaluating their string representations into lists, 
    and prints the time taken to load the dataset.
    """
    load_time = time.time()
    df = pd.read_csv(csv_path)
    df["Keywords"] = df["Keywords"].apply(lambda x: eval(x) if isinstance(x, str) else [])
    df["Weights"] = df["Weights"].apply(lambda x: eval(x) if isinstance(x, str) else [])
    print(f"Dataset Loaded: {csv_path}")
    print(f"Dataset Load Time: {time.time() - load_time}")
    return df


