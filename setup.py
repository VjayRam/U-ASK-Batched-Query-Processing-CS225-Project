from setuptools import setup


def readme():
    with open("README.md") as f:
        return f.read()


setup(
    name="U-ASK",
    version="0.0.1",
    description="""U-ASK is a unified indexing and query processing for kNN spatial-keyword queries supporting negative
keyword predicates (presented in ACM SIGSPATIAL 2022). This project uses U-ASK to support other
types of spatial-keyword queries. Given the U-Ask paper cited below:
> Liu, Y., & Magdy, A. (2022). U-ASK: a unified architecture for kNN spatial-keyword queries supporting negative keyword predicates. In Proceedings of the 30th International Conference on Advances in Geographic Information Systems (SIGSPATIAL '22). Article 40, 1–11""",
    long_description=readme(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 5 - Development/Stable",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9.6",
        "Operating System :: OS Independent",
    ],
    url="https://github.com/VjayRam/SpatialComputing-Project",
    authors=["Vijay Ram Enaganti", "Manoj Manjunatha","Anirudh Nittur Venkatesh"],
    author_email=["venag001@ucr.edu","mmanj008@ucr.edu","anitt003@ucr.edu"],
    packages=["benchmark","index","queries"],
    install_requires=[],
    include_package_data=True,
)