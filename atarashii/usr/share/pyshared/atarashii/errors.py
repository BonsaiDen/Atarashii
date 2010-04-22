

# Python error handling --------------------------------------------------------
# ------------------------------------------------------------------------------
import sys
import os
import locale
import traceback
import time

from __init__ import __version__ as VERSION

from constants import CRASH_LOG_FILE, ERROR_LOG_FILE, CRASH_FILE, START_TIME

# Catch python errors which crash Atarashii
def crash_exit():
    try:
        if sys.last_traceback is None:
            return False
    
    except AttributeError:
        return False
    
    # Set date format to english
    locale.setlocale(locale.LC_TIME, 'C')
    
    # Save the crashlog
    trace = traceback.extract_tb(sys.last_traceback)
    with open(CRASH_LOG_FILE, 'ab') as f:
        error = '''Atarashii %s\nStarted at %s\nCrashed at %s\nTraceback:\n''' \
                % (VERSION,
                   time.strftime('%a %b %d %H:%M:%S +0000 %Y',
                   time.gmtime(START_TIME)),
                   
                   time.strftime('%a %b %d %H:%M:%S +0000 %Y',
                   time.gmtime()))
        
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
    locale.setlocale(locale.LC_TIME, 'C')
    with open(ERROR_LOG_FILE, 'ab') as f:
        f.write('%s %s\n' \
                % (time.strftime('%a %b %d %H:%M:%S +0000 %Y', time.gmtime()),
                   error))
    
    locale.setlocale(locale.LC_TIME, '')

