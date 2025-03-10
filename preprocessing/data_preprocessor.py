import os
import pandas as pd
import math

def load_dataset(data_folder):
    """
    Load and parse the dataset from multiple folders containing text files.
    
    Args:
        data_folder (str): Path to the root dataset directory.
    Returns:
        pd.DataFrame: Structured dataset with columns - ObjectID, Latitude, Longitude, Keywords, Weights, FullText.
    """
    data = []
    for folder in os.listdir(data_folder):
        folder_path = os.path.join(data_folder, folder)
        print(f"Loading data from {folder_path}...")
        if os.path.isdir(folder_path):  
            for file in os.listdir(folder_path):
                file_path = os.path.join(folder_path, file)
                print(f"Loading data from {file_path}...")
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        parts = line.strip().split()
                        if len(parts) < 4:
                            continue  
                        
                        object_id = int(parts[0])
                        latitude = float(parts[1])
                        longitude = float(parts[2])
                        num_keywords = int(parts[3])
                        keywords = []
                        weights = []
                        for i in range(num_keywords):
                            keyword = parts[4 + i * 2]
                            weight = float(parts[5 + i * 2])
                            keywords.append(keyword)
                            weights.append(weight)
                        full_text = parts[5 + num_keywords * 2:]
                        data.append({
                            "ObjectID": object_id,
                            "Latitude": latitude,
                            "Longitude": longitude,
                            "Keywords": keywords,
                            "Weights": weights,
                            "FullText": full_text
                        })
    df = pd.DataFrame(data)
    return df 

def split_and_save_data(df, sizes, base_filename="split_data"):
    """
    Split the dataframe into different subsets based on the given sizes and save as CSV.
    
    Args:
        df (pd.DataFrame): DataFrame to split.
        sizes (list): List of percentages (0-100) for splitting the dataset.
        base_filename (str): Base name for the output CSV files.
    """
    total_records = len(df)
    
    for size in sizes:
        split_size = math.ceil((size / 100) * total_records)  # Get the split size based on percentage
        split_data = df.head(split_size)  # Get the subset of data
        
        filename = f"{base_filename}_{size}%.csv"
        split_data.to_csv(filename, index=False)
        print(f"Saved {size}% data to {filename}")

if __name__ == "__main__":
    dataset_path = "U-ask_data/"  
    df = load_dataset(dataset_path)
    
    print(df.head()) 
    print(f"Total Records Loaded: {len(df)}")
    
    # Specify the percentages for splitting the dataset
    split_sizes = [100]
    split_and_save_data(df, split_sizes)
