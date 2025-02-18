import matplotlib.pyplot as plt

class ResultsAnalysis:
    """
    This class provides methods to analyze and visualize the results of spatial computing queries.

    Methods:
    plot_results(results, title="Query Performance"): Plots a bar chart of the query performance results.
    """
    @staticmethod
    def plot_results(results, title="Query Performance"):
        plt.figure(figsize=(10,5))
        plt.bar(results.keys(), results.values(), color='skyblue')
        plt.xlabel("Query Type")
        plt.ylabel("Execution Time (s)")
        plt.title(title)
        plt.show()

    @staticmethod
    def plot_line_results(results, title="Query Performance"):
        plt.figure(figsize=(10,5))
        plt.plot(results.keys(), results.values(), color='skyblue')
        plt.xlabel("Dataset Size")
        plt.ylabel("Execution Time (s)")
        plt.title(title)
        plt.show()