from setuptools import setup, find_packages

setup(
    name="mincal",
    version="0.0.1",
    packages=find_packages(include=["mincal", "mincal.*"]),
    install_requires=[
        "selenium",
        "selenium-wire",
        "blinker==1.7.0"],
    python_requires=">=3.6",
)