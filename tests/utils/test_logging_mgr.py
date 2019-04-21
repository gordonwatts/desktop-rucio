# Tests for the logging manager

from src.utils.logging_mgr import logging_mgr
import pytest
import shutil
import tempfile
import os

@pytest.fixture()
def lmgr():
    'Setup status temp directory, and then remove it'
    loc = "{0}/desktop-rucio-testing".format(tempfile.gettempdir())
    if os.path.exists(loc):
        shutil.rmtree(loc)
    os.mkdir(loc)
    yield logging_mgr(location=loc)
    shutil.rmtree(loc)

def test_no_log(lmgr):
    assert None is lmgr.get_log('bogus')

def test_oneline_log(lmgr):
    lmgr.log('bogus', 'hi there')
    log = lmgr.get_log('bogus')
    assert 1 == len(log)
    assert "hi there" in log[0]

def test_twoline_log(lmgr):
    lmgr.log('bogus', 'hi there')
    lmgr.log('bogus', 'no way')

    log = lmgr.get_log('bogus')
    assert 2 == len(log)
    assert "hi there" in log[0]
    assert "no way" in log[1]

def test_twoline_log_at_once(lmgr):
    lmgr.log('bogus', ['hi there', 'no way'])

    log = lmgr.get_log('bogus')
    assert 2 == len(log)
    assert "hi there" in log[0]
    assert "no way" in log[1]

def test_list_of_logs_no_log(lmgr):
    assert 0 == len(lmgr.get_available_logs())

def test_list_of_logs_one(lmgr):
    lmgr.log('bogus', 'hi there')
    logs = lmgr.get_available_logs()
    assert 1 == len(logs)
    assert "bogus" == logs[0]

def test_list_of_logs_two(lmgr):
    lmgr.log('bogus1', 'hi there')
    lmgr.log('bogus2', 'you me')
    logs = lmgr.get_available_logs()
    assert 2 == len(logs)
    assert 'bogus1' in logs
    assert 'bogus2' in logs

def test_raw_ctor():
    l = logging_mgr()