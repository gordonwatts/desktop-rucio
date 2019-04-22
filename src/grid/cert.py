# Code to get the grid cert
from src.utils.status_mgr import status_mgr
from src.utils.logging_mgr import logging_mgr
from src.utils.runner import runner

import time

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

    def run_registration_loop(self, executor=None, sleep_func=None, quit_func=None):
        '''
        Run the registration in a continuous loop. Assume every 11 hours we need to
        re-do the registration.
        '''
        # Allow injection for sleep so we can dummy this out in a test.
        sleep_me = time.sleep if sleep_func is None else sleep_func

        # Set the status when we start. Assume nothing is working when we arrive here.
        self._status.save_status('grid_cert', {'is_good': False, 'status': 'acquiring'})

        # Now a loop
        while True:
            # Terminate?
            if quit_func is not None:
                if quit_func():
                    return

            # Try the registration.
            sleep=11*60*60
            if not self.register():
                sleep = 5*60
            
            # Now, sleep.
            sleep_me(sleep)
