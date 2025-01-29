import os
import pandas as pd

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
        if os.path.isdir(folder_path):  # Ensure it's a folder
            for file in os.listdir(folder_path):
                file_path = os.path.join(folder_path, file)
                print(f"Loading data from {file_path}...")
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        parts = line.strip().split()
                        if len(parts) < 4:
                            continue  # Skip malformed lines
                        
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

    # Convert to Pandas DataFrame
    df = pd.DataFrame(data)
    return df

# Example usage
if __name__ == "__main__":
    dataset_path = "dataset/"  # Change this to the actual dataset directory
    df = load_dataset(dataset_path)
    
    print(df.head())  # Display first few rows
    print(f"Total Records Loaded: {len(df)}")

    df.to_csv("dataset.csv", index=False)  # Save to CSV file
