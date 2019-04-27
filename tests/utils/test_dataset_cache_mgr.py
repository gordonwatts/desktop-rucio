# Tests for the dataset manager

from src.utils.dataset_cache_mgr import dataset_cache_mgr, dataset_listing_info
from src.grid.rucio import RucioFile
from tests.grid.utils_for_tests import simple_dataset, nonexistant_dataset
import pytest
import tempfile
import shutil
import os

@pytest.fixture()
def local_cache():
    'Setup cache temp directory, and then remove it when done'
    loc = "{0}/desktop-rucio-cache-testing".format(tempfile.gettempdir())
    if os.path.exists(loc):
        shutil.rmtree(loc)
    os.mkdir(loc)
    yield dataset_cache_mgr(location=loc)
    shutil.rmtree(loc)

def test_dataset_cache_mgr_ctor():
    dataset_cache_mgr()

def test_ds_listing_cache_hit(local_cache, simple_dataset):
    local_cache.save_listing(simple_dataset)
    assert None is not local_cache.get_listing(simple_dataset.Name)

def test_ds_listing_roundtrip(local_cache, simple_dataset):
    local_cache.save_listing(simple_dataset)
    ds_back = local_cache.get_listing(simple_dataset.Name)
    assert simple_dataset.Name == ds_back.Name
    assert simple_dataset.Expiration == ds_back.Expiration
    assert len(simple_dataset.FileList) == len(ds_back.FileList)
    for f in zip(simple_dataset.FileList, ds_back.FileList):
        assert f[0].filename == f[1].filename
        assert f[0].size == f[1].size
        assert f[0].events == f[1].events 

def test_ds_listing_cache_miss(local_cache):
    assert None is local_cache.get_listing("bogus_name")

def test_ds_empty(local_cache, nonexistant_dataset):
    local_cache.save_listing(nonexistant_dataset)
    ds_back = local_cache.get_listing(nonexistant_dataset.Name)
    assert None is ds_back.FileList