# Tests for the status manager

from src.utils.status_mgr import status_mgr
import pytest
import shutil
import tempfile
import os

@pytest.fixture()
def smgr():
    'Setup status temp directory, and then remove it'
    loc = "{0}/desktop-rucio-testing".format(tempfile.gettempdir())
    if os.path.exists(loc):
        shutil.rmtree(loc)
    os.mkdir(loc)
    yield status_mgr(location=loc)
    shutil.rmtree(loc)

def test_no_status(smgr):
    assert 0 == len(smgr.current_status())

def test_stash_one_status(smgr):
    st = {"is_good": True, "message": "hi there"}
    smgr.save_status("part1", st)

    status = smgr.current_status()
    assert 1 == len(status)
    assert "part1" in status
    assert "is_good" in status["part1"]
    assert "message" in status["part1"]
    assert status["part1"]["is_good"]
    assert "hi there" == status["part1"]["message"]

def test_stash_two_status(smgr):
    st1 = {"is_good": True, "message": "m1"}
    st2 = {"is_good": True, "message": "m1", "forK": 25}
    smgr.save_status("st1", st1)
    smgr.save_status("st2", st2)

    status = smgr.current_status()

    assert 2 == len(status)
    assert 2 == len(status["st1"])
    assert 3 == len(status["st2"])

def test_check_status_value(smgr):
    smgr.save_status("st1", {"is_good": True})

    assert None == smgr.status_value("st2", "is_good")
    assert None == smgr.status_value("st1", "is__good")
    assert smgr.status_value("st1", "is_good") is True

def test_check_status_value_with_default(smgr):
    smgr.save_status("st1", {"is_good": True})

    assert False == smgr.status_value("st2", "is_good", default=False)
    assert False == smgr.status_value("st1", "is__good", default=False)
    assert smgr.status_value("st1", "is_good", default=False) is True
