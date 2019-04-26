# Test out everything with datasets.

from src.grid.datasets import dataset_mgr

import pytest

def test_look_for_good_dataset():
    'Queue and look for a good dataset'
    assert False

def test_look_for_good_dataset_that_takes_time():
    'Queue and look for a good dataset that takes a few queries to show up with results'
    assert False

def test_two_queries_for_good_dataset():
    'Make sure second query does not trigger second web download'
    assert False

def test_query_for_bad_dataset():
    'Ask for a bad dataset, and get back a null'
    assert False

def test_query_for_bad_dataset_retrigger():
    'After a bad dataset has aged, automatically queue a new query'
    assert False

def test_ask_non_query_dataset():
    'Ask for a dataset we have not sent in a query for'
    assert False
