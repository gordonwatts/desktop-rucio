# Some common utilities for using in tess.

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

# TODO: We really do not need this
class run_dummy_single:
    def __init__(self, success, lines):
        self._result = exe_result(success, success == 0, lines)

    def shell_execute(self, cmd, log_callback):
        if log_callback is not None:
            for l in self._result.shell_output:
                log_callback(l)
        return self._result

class run_dummy_multiple:
    '''Enable a conversation band and forth'''
    def __init__(self, responses):
        self._responses = responses

    def shell_execute(self, cmd, log_func = None):
        # Make sure we have the command.
        assert cmd in self._responses

        # Got it, now feed back the info in there.
        lines = [l for l_grp in self._responses[cmd]['shell_output'] for l in str.splitlines(l_grp)]
        #lines = l for l in str.splitlines(l_grp): for l_grp in self._responses[cmd]['shell_output']
        if log_func is not None:
            for l in lines:
                log_func(l)
        return exe_result(self._responses[cmd]['shell_result'], self._responses[cmd]['shell_result']==0, lines)

### For help with certificate grabbing
@pytest.fixture()
def cert_good_runner():
    'We will successfully register the thing'
    lines = ['Enter GRID pass phrase for this identity:Contacting lcg-voms2.cern.ch:15001 [/DC=ch/DC=cern/OU=computers/CN=lcg-voms2.cern.ch] "atlas"...',
              'Error contacting lcg-voms2.cern.ch:15001 for VO atlas: Remote host closed connection during handshake',
              'Remote VOMS server contacted succesfully.',
              '',
              '',
              'Created proxy in /usr/usercertfile.',
              '',
              'Your proxy is valid until Mon Apr 22 10:20:03 UTC 2019]']
    yield run_dummy_single(0, lines)
