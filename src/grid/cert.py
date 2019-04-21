# Code to get the grid cert
from src.utils.status_mgr import status_mgr
from src.utils.logging_mgr import logging_mgr
from src.utils.runner import runner

class cert:
    '''
    Drives registration of a grid certificate
    '''
    def __init__ (self, log:logging_mgr = None, status:status_mgr = None):
        self._log = logging_mgr() if log is None else log
        self._status = status_mgr() if status is None else status

    def mgr_status(self):
        return self._status

    def mgr_log(self):
        return self._log

    def register(self, executor=None):
        '''
        Attempt a registration. This is done syncronsously, and might take a while
        to complete!

        executor    If None use default, otherwise use something else to run the command

        returns:

        success - True if it happened, false otherwise.
        '''
        run = executor if executor is not None else runner()

        result = run.shell_execute('echo $GRID_PASSWORD | voms-proxy-init -voms $GRID_VOMS',
                    lambda l: self._log.log('grid_cert', l))

        # Set our status depending on what happened.
        self._status.save_status('grid_cert', {'is_good': result.shell_status})

        # Let the calling guy know how we did.
        return result.shell_status
