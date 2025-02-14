
from index.teq_index import TEQIndex
from queries.power import POWERQueryProcessor
from utils.dataloader import load_dataset
import time

def query_runner(csv_name):
    bounds = (0, 0, 200, 200)  # Define Quadtree boundary
    teq = TEQIndex(bounds)
    dataset_path = "preprocessing/"+csv_name
    print("Loading Dataset")
    data = load_dataset(dataset_path) 
    print("Dataset Loaded total record:", data.shape[0])
    for _, row in data.iterrows():
        teq.add_object(row['ObjectID'], (row['Latitude'], row['Longitude']), row['Keywords'],row['FullText'])

    power = POWERQueryProcessor(teq)
    random_data = data.sample(n=1).iloc[0]
    start = time.time()
    # query = {"location": (random_data['Latitude'], random_data['Longitude']), "positive_keywords":row['Keywords'] , "negative_keywords": row['Keywords'][0], "lambda": 0.5, "k": 5}
    # results = power.process_query(location=query["location"], positive_keywords=query["positive_keywords"], negative_keywords=query["negative_keywords"], k=query["k"], lambda_factor=query["lambda"])
   # 9.02579,7.47525,"['voice', 'back']","[0.5, 0.5]","['voice', 'back']"
    results = power.process_query(location=(9.02579,7.47525), positive_keywords=["voice"], negative_keywords=["back"], k=5, lambda_factor=0.5)

    print("Time"+csv_name+":"+str(time.time() - start))
    print(results)
    # results = {  "TKQN": Benchmark.run(power, data,query)}
    # ResultsAnalysis.plot_results(results)