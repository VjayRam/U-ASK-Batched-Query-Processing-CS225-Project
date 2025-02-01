import pandas as pd
import time

def load_dataset(csv_path):
    load_time = time.time()
    df = pd.read_csv(csv_path)
    df["Keywords"] = df["Keywords"].apply(lambda x: eval(x) if isinstance(x, str) else [])
    df["Weights"] = df["Weights"].apply(lambda x: eval(x) if isinstance(x, str) else [])
    print(f"Dataset Loaded: {csv_path}")
    print(f"Dataset Load Time: {time.time() - load_time}")
    return df


# Example usage
if __name__ == "__main__":
    dataset_path = "data/dataset.csv"  # Change this to the actual dataset directory
    df = load_dataset(dataset_path)
    
    print(df.head())  # Display first few rows
    print(f"Total Records Loaded: {len(df)}")

    # df.to_csv("dataset.csv", index=False)  # Save to CSV file
