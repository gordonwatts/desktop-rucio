# Supply the status of everything we have currently running.

import hug
from src.utils.status_mgr import status_mgr

@hug.get('/status')
def hello():
    r'''
    Return the complete status of the system.
    '''
    return status_mgr().current_status()

