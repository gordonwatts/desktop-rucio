# Test file for hug

import hug

@hug.get('/hello')
def hello(name: str):
    r'''
    Does a hello message

    name: name the hello message should be addressed to.
    '''
    return "Hi {name}".format(**locals())
