# Test the grid certificate methods.

from src.grid.cert import cert
from src.utils.runner import exe_result

import pytest

class dummy_logger:
    def __init__(self):
        self.name = None
        self.lines = []
        pass

    def got_log(self, name):
        return name == self.name

    def log(self, name, line):
        self.name = name
        self.lines.append(line)


class dummy_status:
    def __init__ (self):
        self._name = None
        self._dict = {}

    def got(self, name):
        return self._name == name

    def save_status (self, name, status_info):
        self._name = name
        self._dict = status_info

    def is_good(self):
        return self._dict['is_good']

@pytest.fixture()
def gcert():
    yield cert(log=dummy_logger(), status=dummy_status())

class run_dummy:
    def __init__(self, success, lines):
        self._result = exe_result(success, success == 0, lines)

    def shell_execute(self, cmd, log_callback):
        if log_callback is not None:
            for l in self._result.shell_output:
                log_callback(l)
        return self._result

@pytest.fixture()
def good_runner():
    'We will successfully register the thing'
    lines = ['Enter GRID pass phrase for this identity:Contacting lcg-voms2.cern.ch:15001 [/DC=ch/DC=cern/OU=computers/CN=lcg-voms2.cern.ch] "atlas"...',
              'Error contacting lcg-voms2.cern.ch:15001 for VO atlas: Remote host closed connection during handshake',
              'Remote VOMS server contacted succesfully.',
              '',
              '',
              'Created proxy in /usr/usercertfile.',
              '',
              'Your proxy is valid until Mon Apr 22 10:20:03 UTC 2019]']
    yield run_dummy(0, lines)

@pytest.fixture()
def bad_runner_password():
    'We will fail to re register.'
    lines = ["Enter GRID pass phrase for this identity:Credentials couldn't be loaded [/root/.globus/userkey.pem, /root/.globus/usercert.pem]: Error decrypting private key: the password is incorrect or the PEM data is corrupted.",
             "No credentials found!"]
    yield run_dummy(1, lines)

@pytest.fixture()
def bad_runner_voms():
    'We will fail to re register.'
    lines = ["VOMS server for VO atlassss is not known! Check your vomses configuration."]
    yield run_dummy(1, lines)

@pytest.fixture()
def bad_runner_bad_internet():
    'We will fail to re register.'
    lines = ['Enter GRID pass phrase for this identity:Contacting voms2.cern.ch:15001 [/DC=ch/DC=cern/OU=computers/CN=voms2.cern.ch] "atlas"...',
            'Error contacting voms2.cern.ch:15001 for VO atlas: voms2.cern.ch',
            'Error contacting voms2.cern.ch:15001 for VO atlas: voms2.cern.ch',
            'Error contacting voms2.cern.ch:15001 for VO atlas: REST and legacy VOMS endpoints failed.',
            'Contacting lcg-voms2.cern.ch:15001 [/DC=ch/DC=cern/OU=computers/CN=lcg-voms2.cern.ch] "atlas"...',
            'Error contacting lcg-voms2.cern.ch:15001 for VO atlas: lcg-voms2.cern.ch',
            'Error contacting lcg-voms2.cern.ch:15001 for VO atlas: lcg-voms2.cern.ch',
            'Error contacting lcg-voms2.cern.ch:15001 for VO atlas: REST and legacy VOMS endpoints failed.',
            'None of the contacted servers for atlas were capable of returning a valid AC for the user.',
            "User's request for VOMS attributes could not be fulfilled."]
    yield run_dummy(1, lines)

def test_ctor():
    _ = cert()

def test_register(gcert, good_runner):
    assert True is gcert.register(executor=good_runner)
    assert True == gcert.mgr_status().got('grid_cert')
    assert True == gcert.mgr_status().is_good()
    assert True == gcert.mgr_log().got_log('grid_cert')

def test_fail_register(gcert, bad_runner_password):
    assert False is gcert.register(executor=bad_runner_password)
    assert True == gcert.mgr_status().got('grid_cert')
    assert False == gcert.mgr_status().is_good()
    assert True == gcert.mgr_log().got_log('grid_cert')
