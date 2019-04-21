# Logging manager - simple track logs in files.
# Designed not to be so much as efficient as being able to remember everything if there
# is a crash.
import os
import tempfile

class logging_mgr:
    r'''
    Track log files, date stamp everything
    '''
    def __init__(self, location = None):
        '''
        Initialize the logging manager.

        loc: If loc is None, default to the temp directory.
        '''
        # Get our path all set up
        if location is None:
            location = "{0}/desktop-rucio-logs".format(tempfile.gettempdir())
        if not os.path.exists(location):
            os.mkdir(location)
        self._loc = location

    def get_logfile_name(self, log_name):
        'Return the full path of a log file for the given name'
        return "{self._loc}/{log_name}.log".format(**locals())


    def log(self, log_name, log_lines):
        '''
        Record log_lines in the log_name log. Everything will be timestamped.

        log_name: Name of the log
        log_lines: a string (single line) or an iterable list of strings
        '''
        with open(self.get_logfile_name(log_name), 'a') as f:
            if type(log_lines) is str:
                f.write(log_lines + '\n')
            else:
                f.writelines([l + '\n' for l in log_lines])

    def get_log(self, log_name):
        '''
        Return the contents of the log as a list of lines.

        log_name: The name of the log

        Returns:
        [l1, l2, l3...]: List of lines
        None if the log doesn't exist at all.
        '''
        log_filename = self.get_logfile_name(log_name)
        if not os.path.exists(log_filename):
            return None

        with open(log_filename, 'r') as f:
            return f.readlines()
    
    def get_available_logs(self):
        'return all available log names'
        return [os.path.splitext(f)[0] for f in os.listdir(self._loc)]