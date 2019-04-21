# Controller that returns log files

import hug
from src.utils.logging_mgr import logging_mgr

@hug.get('/logs')
def get_logs(name:str = None):
    '''
    Return the contents of logs

    if name is not provided return a list of logs on the system
    Otherwise return the log requested.
    '''
    # Catalog?
    if name is None:
        return logging_mgr().get_available_logs()
    
    l = logging_mgr().get_log(name)
    return l if l is not None else []
