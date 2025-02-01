import matplotlib.pyplot as plt

# Results Analysis
class ResultsAnalysis:
    @staticmethod
    def plot_results(results, title="Query Performance"):
        plt.figure(figsize=(10,5))
        plt.bar(results.keys(), results.values(), color='skyblue')
        plt.xlabel("Query Type")
        plt.ylabel("Execution Time (s)")
        plt.title(title)
        plt.show()
