# Test out everything with datasets.

from src.grid.datasets import dataset_mgr, DatasetQueryStatus
from tests.grid.utils_for_tests import simple_dataset
from time import sleep
import datetime

import pytest

@pytest.fixture()
def rucio_2file_dataset(simple_dataset):
    class rucio_dummy:
        def __init__(self, ds):
            self._ds = ds
            self.CountCalled = 0

        def get_file_listing(self, ds_name):
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

        def get_file_listing(self, ds_name):
            self.CountCalled += 1
            if self.CountCalled < 5:
                raise BaseException("Please Try again Due To Internet Being Out")
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

        def get_listing(self, ds_name):
            if ds_name in self._ds_list:
                return self._ds_list[ds_name]
            return None

        def save_listing(self, ds_info):
            self._ds_list[ds_info.Name] = ds_info

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

    # Make sure we didn't re-query for this, and the expiration date is not set.
    assert 1 == rucio_2file_dataset.CountCalled == 1
    info = cache_empty.get_listing(simple_dataset.Name)
    assert None is info.Expiration

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
    assert (datetime.datetime.now() + datetime.timedelta(minutes=60)) == info.Expiration

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

# def test_two_queries_for_good_dataset():
#     'Make sure second query does not trigger second web download'
#     dm = dataset_mgr(ds_mgr)
#     _ = dm.get_ds_contents(simple_dataset.Name)
#     _ = dm.get_ds_contents(simple_dataset.Name)
#     # Now, make sure that only one query occurred.
#     assert False

# def test_query_for_bad_dataset_retrigger():
#     'After a bad dataset has aged, automatically queue a new query'
#     assert False

# def test_ask_non_query_dataset():
#     'Ask for a dataset we have not sent in a query for'
#     assert False
