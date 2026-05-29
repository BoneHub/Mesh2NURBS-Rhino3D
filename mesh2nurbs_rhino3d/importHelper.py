def importPackages():
    import rhinoscriptsyntax as rs  # type: ignore
    import Rhino.Geometry as rg  # type: ignore
    import scriptcontext  # type: ignore
    import Rhino  # type: ignore
    import numpy as np  # type: ignore
    import time
    import point_cloud_utils as pcu  # type: ignore
    import os
    import csv
    import shutil
    import pandas as pd  # type: ignore
    from vedo import Points, show, Plotter, Sphere, Text2D, settings, write, Assembly  # type: ignore
    import matplotlib.colors as mcolors  # type: ignore
    import matplotlib.cm as cm  # type: ignore
    import matplotlib.pyplot as plt_mpl  # type: ignore
    from scipy.spatial import KDTree  # type: ignore
