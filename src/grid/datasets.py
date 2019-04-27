# Manage everything having to do with the organization
# of datasets.
from src.grid.rucio import RucioFile, rucio
from src.utils.dataset_cache_mgr import dataset_cache_mgr, dataset_listing_info
from typing import List, Optional, Tuple
import datetime
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, wait

DatasetQueryStatus = Enum('DatasetQueryStatus', 'does_not_exist, query_queued, results_valid')


class dataset_mgr:
    r'''
    Manages datasets:
      - What files are in them (on the grid).

    We do nothing with synced datasets!
    '''
    def __init__(self, data_mgr:dataset_cache_mgr, rucio_mgr: Optional[rucio] = None):
        '''
        Setup a dataset_mgr

        Arguments:
        rucio_mgr           Interface to query rucio directly to get back dataset file results.
        '''
        # We want to query rucio one dataset at a time.
        self._exe = ThreadPoolExecutor(max_workers=5)
        self._rucio = rucio_mgr if rucio_mgr is not None else rucio()
        self._cache_mgr = data_mgr

    def get_ds_contents(self, ds_name: str, maxAge: Optional[datetime.timedelta] = None, maxAgeIfNotSeen: Optional[datetime.timedelta] = None) -> Tuple[DatasetQueryStatus, Optional[List[RucioFile]]]:
        '''
        Return the list of files that are in a dataset if they are in our local cache. If not, then queue a query to
        rucio to get the actual file contents. The results have age checks, which will trigger a re-query.

        If the dataset does not exist on the grid, it will be placed into our local cache, but given a 1 hour expiration
        time (so in an hour you can re-query and it will automatically re-query rucio).

        Arguments
        name              The rucio fully qualified name of the dataset
        maxAge            If None - any local results are returned, and if no results are present a query is started
                          if a `timedelta` then:
                              If no results present a query is queued.
                              If there are local results, then a query is queued if they are older than timedelta.
        maxAgeIfNotSeen   maxAge takes precedence. If maxAgeIfNotSeen is not null, and there are cached local results:
                              If the results point to a dataset that is valid, then the file list is returned.
                              If last time the cached dataset was queried it wasn't found, and it was queired a more recently
                                  than maxAgeIfNotSeen, then return does not exist.
                              Otherwise re-query rucio to see if the dataset has now appeared.

        Returns
        status        Status of the returned results (see DatasetQueryStatus) and below:
        files         Depends on the status:
                          does_not_exist - files will be None, and the dataset was not found on the last query to rucio.
                          query_queued - files will be None, and a query is pending to update the results
                          results_valid - files will be a list of all files in the dataset. 
                              Empty Dataset: The dataset is empty if the list has len()==0.
                              Dataset with files: The list will have an entry per file
        '''
        # See if the listing exists, if so, return it.
        listing = self._cache_mgr.get_listing(ds_name)
        if listing is not None:
            status = DatasetQueryStatus.results_valid if listing.FileList is not None else DatasetQueryStatus.does_not_exist
            return (status, listing.FileList)
            
        # Queue up run against rucio to find out what is in this dataset.
        f = self._exe.submit(dataset_mgr.query_rucio, self, ds_name)

        # Return the fact that the query has been queued.
        return (DatasetQueryStatus.query_queued, None)

    def query_rucio(self, ds_name:str):
        '''
        Run a query against rucio and then save the results.
        '''
        r = self._rucio.get_file_listing(ds_name)
        # If the dataset doesn't exist, then we need to set the expiration time.
        expire = (datetime.datetime.now() + datetime.timedelta(minutes=60)) if r is None else None
        self._cache_mgr.save_listing(dataset_listing_info(ds_name, expire, r))
