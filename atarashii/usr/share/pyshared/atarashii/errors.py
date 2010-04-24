

# Python error handling --------------------------------------------------------
# ------------------------------------------------------------------------------
import sys
import os
import locale
import traceback
import time

from __init__ import __version__ as VERSION

from constants import CRASH_LOG_FILE, ERROR_LOG_FILE, CRASH_FILE, START_TIME

def format_time(date, format='%a %b %d %H:%M:%S +0000 %Y'):
    locale.setlocale(locale.LC_TIME, 'C')
    string = time.strftime(format, date)
    locale.setlocale(locale.LC_TIME, '')
    return string

def crash_exit():
    try:
        if sys.last_traceback is None:
            return False
    
    except AttributeError:
        return False
    
    with open(CRASH_LOG_FILE, 'ab') as f:
        error = '''Atarashii %s\nStarted at %s\nCrashed at %s\nTraceback:\n''' \
                % (VERSION, format_time(time.gmtime(START_TIME)),
                   format_time(time.gmtime()))
        
        trace = traceback.extract_tb(sys.last_traceback)
        f.write(error + '\n'.join(traceback.format_list(trace)) + '\n')
    
    sys.exit(70) # os.EX_SOFTWARE

def crash_file(mode, data=None):
    try:
        if mode:
            with open(CRASH_FILE, 'wb') as f:
                f.write(str(data))
        
        elif os.path.exists(CRASH_FILE):
            os.unlink(CRASH_FILE)
    
    except (OSError, IOError):
        log_error('IO on crashfile failed')

def log_error(error):
    with open(ERROR_LOG_FILE, 'ab') as f:
        f.write('%s %s\n' % (format_time(time.gmtime()), error))

