# Manage the cache on disk
# - Contents of datasets
# - What datasets we have
#

from datetime import datetime
from src.grid.rucio import RucioFile
from typing import List, Optional
import os
import tempfile
import json
import pickle

class dataset_listing_info:
    '''
    Simple object that contains a list of files in the dataset
    '''
    def __init__ (self, name: str, expiration: Optional[datetime], files: List[RucioFile]):
        '''
        Initialize a dataset file listing.

        Arguments
        expiration:     This listing should be ignored after this date. If None, then it never expires
        flies:          Listing of files. None means the dataset does not exist. Empty list means an empty dataset.
        '''
        self.Name = name
        self.Expiration = expiration
        self.FileList = files

class dataset_cache_mgr:
    r'''
    Manage the cache that contains the datasets we are going to be storing.
    '''

    def __init__(self, location=None):
        '''
        Initialize the dataset cache.

        Arguments:
        location            If given, use that as the proper location of the cache.
        '''
        self._loc = location if location is not None else "{0}/desktop-rucio-cache".format(tempfile.gettempdir())
        if not os.path.exists(self._loc):
            os.mkdir(self._loc)

    def _get_filename(self, dirname, fname_stub):
        d = "{self._loc}/{dirname}".format(**locals())
        if not os.path.exists(d):
            os.mkdir(d)
        return "{d}/{fname_stub}.pickle".format(**locals())

    def save_listing (self, ds_listing: dataset_listing_info) -> None:
        'Save a listing to the cache'
        with open(self._get_filename("cache", ds_listing.Name), 'wb') as f:
            pickle.dump(ds_listing, f)
        self._remove_query_mark(ds_listing.Name)

    def get_listing(self, name) -> dataset_listing_info:
        'Return the listing. None if the listing does not exist'
        f_name = self._get_filename("cache", name)
        if not os.path.exists(f_name):
            return None
        with open(f_name, 'rb') as f:
            return pickle.load(f)

    def mark_query(self, name) -> None:
        'Mark this dataset name as having a query in progress'
        f_name = self._get_filename("query_in_progress", name)
        with open(f_name, 'w') as f:
            f.write("Query marked in progress " + str(datetime.now()))

    def query_in_progress(self, name) -> bool:
        'Look for the query in progress marker for this dataset'
        f_name = self._get_filename("query_in_progress", name)
        return os.path.exists(f_name)

    def _remove_query_mark(self, name) -> None:
        f_name = self._get_filename("query_in_progress", name)
        if os.path.exists(f_name):
            os.unlink(f_name)

