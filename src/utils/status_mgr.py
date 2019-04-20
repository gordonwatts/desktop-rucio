# Status management stuff
import json
import os

# Default location of status json files
default_file_location = "/tmp/status"

class status_mgr:
    r'''
    Class to help manage the status manager
    '''
    def __init__ (self, location = default_file_location):
        self._loc = location
    
    def current_status(self):
        'Return a dictionary of all statuses in the system'
        all_status = {}
        for fname in [f for f in os.listdir(self._loc) if f.endswith(".json")]:
            with open("{self._loc}/{fname}".format(**locals()), 'r') as fhand:
                d = json.loads(fhand.readline())
                all_status[os.path.basename(os.path.splitext(fname)[0])] = d

        return all_status
    
    def save_status(self, status_name: str, dict_of_items: dict):
        '''
        Save a status under `status_name` to the local directory. The `dict_of_items` is saved
        as json in a file.
        '''
        global default_file_location
        r = json.dumps(dict_of_items)
        with open("{0}/{1}.json".format(self._loc, status_name), 'w') as f:
            f.write(r)

    def status_value(self, status_name, status_value_name, default=None):
        'Return the value of the status pair, and the default if it cannot be found'
        f = "{self._loc}/{status_name}.json".format(**locals())
        if not os.path.exists(f):
            return default

        with open(f, 'r') as fhand:
            d = json.loads(fhand.readline())
            if status_value_name not in d:
                return default
            return d[status_value_name]
        