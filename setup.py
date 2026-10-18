from setuptools import setup, find_packages

setup(
    name="equal-earth-india",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "matplotlib>=3.8.0",
        "cartopy>=0.22.0",
        "shapely>=2.0.0",
        "numpy>=1.24.0",
        "pyproj>=3.6.0"
    ],
    entry_points={
        "console_scripts": [
            "equal-earth=equal_earth.cli:main",
        ],
    },
)
