# setup.py

from setuptools import setup, find_packages  # type: ignore

setup(
    name="rhinoMeshTools",
    version="0.2",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "point_cloud_utils",
        "pandas",
        "scipy",
        "vedo",
        "matplotlib",
    ],
    entry_points={
        "console_scripts": ["mesh2cad = rhinoMeshTools.cli_full:main", "fix-mesh = rhinoMeshTools.cli_fix:main"],
    },
)
