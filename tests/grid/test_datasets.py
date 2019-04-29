# Test out everything with datasets.

from src.grid.datasets import dataset_mgr, DatasetQueryStatus
from tests.grid.utils_for_tests import simple_dataset
from time import sleep
import datetime
import os

import pytest

@pytest.fixture()
def rucio_2file_dataset(simple_dataset):
    class rucio_dummy:
        def __init__(self, ds):
            self._ds = ds
            self.CountCalled = 0
            self._cache_mgr = None

        def get_file_listing(self, ds_name, log_func = None):
            self.CountCalled += 1
            if ds_name == self._ds.Name:
                return self._ds.FileList
            return None

        def download_files(self, ds_name, data_dir):
            if self._cache_mgr is not None:
                self._cache_mgr.add_ds(self._ds)
            self.CountCalled += 1


    return rucio_dummy(simple_dataset)

@pytest.fixture()
def rucio_2file_dataset_take_time(simple_dataset):
    class rucio_dummy:
        def __init__(self, ds):
            self._ds = ds
            self.CountCalled = 0

        def get_file_listing(self, ds_name, log_func = None):
            sleep(0.005)
            self.CountCalled += 1
            if ds_name == self._ds.Name:
                return self._ds.FileList
            return None

    return rucio_dummy(simple_dataset)

@pytest.fixture()
def rucio_2file_dataset_with_fails(simple_dataset):
    class rucio_dummy:
        def __init__(self, ds):
            self._ds = ds
            self.CountCalled = 0

        def get_file_listing(self, ds_name, log_func = None):
            self.CountCalled += 1
            if self.CountCalled < 5:
                raise BaseException("Please Try again Due To Internet Being Out")
            if ds_name == self._ds.Name:
                return self._ds.FileList
            return None

    return rucio_dummy(simple_dataset)

@pytest.fixture()
def rucio_2file_dataset_shows_up_later(simple_dataset):
    class rucio_dummy:
        def __init__(self, ds):
            self._ds = ds
            self.CountCalled = 0

        def get_file_listing(self, ds_name, log_func = None):
            self.CountCalled += 1
            if self.CountCalled < 2:
                return None
            if ds_name == self._ds.Name:
                return self._ds.FileList
            return None

    return rucio_dummy(simple_dataset)

@pytest.fixture()
def cache_empty():
    'Create an empty cache that will save anything saved in it.'
    class cache_good_dummy():
        def __init__(self):
            self._ds_list = {}
            self._in_progress = []
            self._in_download = []
            self._downloaded_ds = {}
        
        def get_download_directory(self):
            return 'totally-bogus'

        def add_ds(self, ds_info):
            self._downloaded_ds[ds_info.Name] = ds_info

        def get_listing(self, ds_name):
            if ds_name in self._ds_list:
                return self._ds_list[ds_name]
            return None

        def save_listing(self, ds_info):
            self._ds_list[ds_info.Name] = ds_info
            self._in_progress.remove(ds_info.Name)

        def mark_query(self, ds_name):
            self._in_progress.append(ds_name)
        def query_in_progress(self, ds_name):
            return ds_name in self._in_progress

        def get_ds_contents(self, ds_name):
            if ds_name in self._downloaded_ds:
                return [f.filename for f in self._downloaded_ds[ds_name].FileList]
            return None

        def mark_downloading(self, ds_name):
            self._in_download.append(ds_name)

        def download_in_progress(self, ds_name):
            return ds_name in self._in_download

        def mark_download_done(self, ds_name):
            self._in_download.remove(ds_name)

    return cache_good_dummy()

def test_dataset_query_queued(rucio_2file_dataset, cache_empty):
    'Queue a dataset'
    dm = dataset_mgr(cache_empty, rucio_mgr=rucio_2file_dataset)
    status, files = dm.get_ds_contents('a_dataset')

    # Should have queued the result since this was a new ds manager
    assert status == DatasetQueryStatus.query_queued
    assert None is files

def wait_some_time(check):
    'Simple method to wait until check returns false. Will wait up to about a second so as not to delay things before throwing an assert.'
    counter = 0
    while check():
        sleep(0.01)
        counter += 1
        assert counter < 100

def test_dataset_query_resolved(rucio_2file_dataset, cache_empty, simple_dataset):
    'Queue and look for a dataset query result'
    dm = dataset_mgr(cache_empty, rucio_mgr=rucio_2file_dataset)
    _ = dm.get_ds_contents(simple_dataset.Name)

    # Wait for the dataset query to run
    wait_some_time(lambda: rucio_2file_dataset.CountCalled == 0)

    # Now, make sure that we get back what we want here.
    status, files = dm.get_ds_contents(simple_dataset.Name)
    assert DatasetQueryStatus.results_valid == status
    assert len(simple_dataset.FileList) == len(files)

    # Make sure we didn't re-query for this.
    assert 1 == rucio_2file_dataset.CountCalled == 1
    info = cache_empty.get_listing(simple_dataset.Name)

def test_query_for_bad_dataset(rucio_2file_dataset, cache_empty, simple_dataset):
    'Ask for a bad dataset, and get back a null'
    dm = dataset_mgr(cache_empty, rucio_mgr=rucio_2file_dataset)
    _ = dm.get_ds_contents('bogus_ds')
    wait_some_time(lambda: rucio_2file_dataset.CountCalled == 0)

    # Make sure it comes back as bad.
    status, files = dm.get_ds_contents('bogus_ds')
    assert DatasetQueryStatus.does_not_exist == status
    assert None is files

    # Make sure that a timeout of an hour has been set on the dataset.
    info = cache_empty.get_listing('bogus_ds')
    assert datetime.datetime.now() == info.Created

def test_look_for_good_dataset_that_fails_a_bunch(rucio_2file_dataset_with_fails, cache_empty, simple_dataset):
    'Queue and look for a good dataset that takes a few queries to show up with results'
    dm = dataset_mgr(cache_empty, rucio_mgr=rucio_2file_dataset_with_fails, seconds_between_retries=0.01)
    _ = dm.get_ds_contents(simple_dataset.Name)

    # Wait for the dataset query to run
    wait_some_time(lambda: rucio_2file_dataset_with_fails.CountCalled < 5)

    # Now, make sure that we get back what we want and that the number of tries matches what we think
    # it should have.
    status, files = dm.get_ds_contents(simple_dataset.Name)
    assert DatasetQueryStatus.results_valid == status
    assert 5 == rucio_2file_dataset_with_fails.CountCalled

def test_two_queries_for_good_dataset(rucio_2file_dataset_take_time, cache_empty, simple_dataset):
    'Make sure second query does not trigger second web download'
    # Query twice, make sure we don't forget as we are doing this!
    dm = dataset_mgr(cache_empty, rucio_mgr=rucio_2file_dataset_take_time)
    _ = dm.get_ds_contents(simple_dataset.Name)
    status, _ = dm.get_ds_contents(simple_dataset.Name)
    assert DatasetQueryStatus.query_queued == status

    # Wait for the dataset query to run
    wait_some_time(lambda: rucio_2file_dataset_take_time.CountCalled == 0)

    # Now, make sure that we get back what we want here.
    status, _ = dm.get_ds_contents(simple_dataset.Name)
    assert DatasetQueryStatus.results_valid == status

    # Make sure we didn't re-query for this, and the expiration date is not set.
    # Make sure to wait long enough for other timing stuff above to fall apart.
    sleep(0.02)
    assert 1 == rucio_2file_dataset_take_time.CountCalled

def test_dataset_appears(rucio_2file_dataset_shows_up_later, cache_empty, simple_dataset):
    'After a bad dataset has aged, automatically queue a new query'
    dm = dataset_mgr(cache_empty, rucio_mgr=rucio_2file_dataset_shows_up_later)
    _ = dm.get_ds_contents(simple_dataset.Name)
    wait_some_time(lambda: rucio_2file_dataset_shows_up_later.CountCalled == 0)
    status, _ = dm.get_ds_contents(simple_dataset.Name)
    assert DatasetQueryStatus.does_not_exist == status

    # Query, but demand a quick re-check
    status, _ = dm.get_ds_contents(simple_dataset.Name, maxAgeIfNotSeen=datetime.timedelta(seconds=0))
    assert DatasetQueryStatus.query_queued == status
    wait_some_time(lambda: rucio_2file_dataset_shows_up_later.CountCalled == 1)
    status, _ = dm.get_ds_contents(simple_dataset.Name)
    assert DatasetQueryStatus.results_valid == status

def test_dataset_always_missing_noretry(rucio_2file_dataset_shows_up_later, cache_empty, simple_dataset):
    'Do not requery for the dataset'
    dm = dataset_mgr(cache_empty, rucio_mgr=rucio_2file_dataset_shows_up_later)
    _ = dm.get_ds_contents(simple_dataset.Name)
    wait_some_time(lambda: rucio_2file_dataset_shows_up_later.CountCalled == 0)
    status, _ = dm.get_ds_contents(simple_dataset.Name)
    assert DatasetQueryStatus.does_not_exist == status

    # Query, but demand a quick re-check
    status, _ = dm.get_ds_contents(simple_dataset.Name, maxAgeIfNotSeen=None)
    assert DatasetQueryStatus.does_not_exist == status
    assert 1 == rucio_2file_dataset_shows_up_later.CountCalled

def test_dataset_always_missing_longretry(rucio_2file_dataset_shows_up_later, cache_empty, simple_dataset):
    'Do not requery for the dataset'
    dm = dataset_mgr(cache_empty, rucio_mgr=rucio_2file_dataset_shows_up_later)
    _ = dm.get_ds_contents(simple_dataset.Name)
    wait_some_time(lambda: rucio_2file_dataset_shows_up_later.CountCalled == 0)
    status, _ = dm.get_ds_contents(simple_dataset.Name)
    assert DatasetQueryStatus.does_not_exist == status

    # Query, but demand a quick re-check
    status, _ = dm.get_ds_contents(simple_dataset.Name, maxAgeIfNotSeen=datetime.timedelta(seconds=1000))
    assert DatasetQueryStatus.does_not_exist == status
    assert 1 == rucio_2file_dataset_shows_up_later.CountCalled

def test_good_dataset_retry(rucio_2file_dataset, cache_empty, simple_dataset):
    'Do a requery for the dataset'
    dm = dataset_mgr(cache_empty, rucio_mgr=rucio_2file_dataset)
    _ = dm.get_ds_contents(simple_dataset.Name)
    wait_some_time(lambda: rucio_2file_dataset.CountCalled == 0)
    status, _ = dm.get_ds_contents(simple_dataset.Name)
    assert DatasetQueryStatus.results_valid == status

    # Query, but demand a quick re-check
    status, _ = dm.get_ds_contents(simple_dataset.Name, maxAge=datetime.timedelta(seconds=0))
    assert DatasetQueryStatus.query_queued == status
    wait_some_time(lambda: rucio_2file_dataset.CountCalled == 1)
    status, _ = dm.get_ds_contents(simple_dataset.Name)
    assert DatasetQueryStatus.results_valid == status

    assert 2 == rucio_2file_dataset.CountCalled

def test_good_dataset_longretry(rucio_2file_dataset, cache_empty, simple_dataset):
    'Do not requery for the dataset'
    dm = dataset_mgr(cache_empty, rucio_mgr=rucio_2file_dataset)
    _ = dm.get_ds_contents(simple_dataset.Name)
    wait_some_time(lambda: rucio_2file_dataset.CountCalled == 0)
    status, _ = dm.get_ds_contents(simple_dataset.Name)
    assert DatasetQueryStatus.results_valid == status

    # Query, but demand a quick re-check
    status, _ = dm.get_ds_contents(simple_dataset.Name, maxAge=datetime.timedelta(seconds=1000))
    assert DatasetQueryStatus.results_valid == status
    assert 1 == rucio_2file_dataset.CountCalled

def test_good_dataset_maxAgeIfNotSeenNoEffect(rucio_2file_dataset, cache_empty, simple_dataset):
    'Do not requery for the dataset'
    dm = dataset_mgr(cache_empty, rucio_mgr=rucio_2file_dataset)
    _ = dm.get_ds_contents(simple_dataset.Name)
    wait_some_time(lambda: rucio_2file_dataset.CountCalled == 0)
    status, _ = dm.get_ds_contents(simple_dataset.Name)
    assert DatasetQueryStatus.results_valid == status

    # Query, but demand a quick re-check
    status, _ = dm.get_ds_contents(simple_dataset.Name, maxAgeIfNotSeen=datetime.timedelta(seconds=0))
    assert DatasetQueryStatus.results_valid == status
    assert 1 == rucio_2file_dataset.CountCalled

def test_dataset_download_query(rucio_2file_dataset, cache_empty, simple_dataset):
    'Queue a download and look for it to show up'
    dm = dataset_mgr(cache_empty, rucio_mgr=rucio_2file_dataset)
    status, files = dm.download_ds(simple_dataset.Name)
    assert files is None
    assert DatasetQueryStatus.query_queued == status

def test_dataset_download_good(rucio_2file_dataset, cache_empty, simple_dataset):
    'Queue a download and look for it to show up'
    rucio_2file_dataset._cache_mgr = cache_empty
    dm = dataset_mgr(cache_empty, rucio_mgr=rucio_2file_dataset)
    _ = dm.download_ds(simple_dataset.Name)

    # Wait for the dataset query to run
    wait_some_time(lambda: rucio_2file_dataset.CountCalled == 0)

    # Now, make sure that we get back what we want here.
    status, files = dm.download_ds(simple_dataset.Name)
    assert DatasetQueryStatus.results_valid == status
    assert len(simple_dataset.FileList) == len(files)

    # Make sure we didn't re-query for this.
    assert 1 == rucio_2file_dataset.CountCalled

# Tests for downloads:
# TODO:
#  Make sure that filenames that come back are relative to the _loc for the dataset.
#  Try to download a non-existant dataset
#  Try to download good ds with a few failures
#  Make sure (?) that the full list of files for a dataset is downloaded - so trigger a lookup when we do the download.
#  Deal with being asked twice
#  limit them to 3 at a time or similar (?)
#  Make sure the download is properly logged.
