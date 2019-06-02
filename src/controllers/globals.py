# Some global things shared in the webserver.

from src.grid.datasets import dataset_mgr
from src.utils.dataset_cache_mgr import dataset_cache_mgr

# Init the dataset manager
dataset_cache = dataset_cache_mgr("/data")
datasets = dataset_mgr(dataset_cache)

# Get the cache prefix
import os
cache_prefix = None if 'CACHE_PREFIX' not in os.environ else os.environ['CACHE_PREFIX']
