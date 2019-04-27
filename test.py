# Test harness for debugging easily.

from tests.grid.test_datasets import test_two_queries_for_good_dataset
from src.grid.rucio import RucioFile
from src.utils.dataset_cache_mgr import dataset_listing_info

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

def rucio_2file_dataset_take_time(simple_dataset):
    class rucio_dummy:
        def __init__(self, ds):
            self._ds = ds
            self.CountCalled = 0

        def get_file_listing(self, ds_name):
            sleep(0.005)
            self.CountCalled += 1
            if ds_name == self._ds.Name:
                return self._ds.FileList
            return None

    return rucio_dummy(simple_dataset)

def cache_empty():
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

def simple_dataset():
    'Create a simple dataset with 2 files in it and no expiration'
    f1 = RucioFile('f1.root', 100, 1)
    f2 = RucioFile('f2.root', 200, 2)
    return dataset_listing_info('dataset1', None, [f1, f2])


test_two_queries_for_good_dataset(rucio_2file_dataset_take_time(simple_dataset()), cache_empty(), simple_dataset())
