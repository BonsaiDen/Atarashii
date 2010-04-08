#  This file is part of Atarashii.
#
#  Atarashii is free software: you can redistribute it and/or
#  modify it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Atarashii is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License along with
#  Atarashii. If not, see <http://www.gnu.org/licenses/>.


# Settings ---------------------------------------------------------------------
# ------------------------------------------------------------------------------
import os
import urllib
import time

from constants import UNSET_SETTING, UNSET_ID_NUM

# File Paths
HOME_DIR = os.path.expanduser('~')
DESKTOP_FILE = os.path.join(HOME_DIR, '.config',
                            'autostart', 'atarashii.desktop')

AUTOSTART_DIR = os.path.join(HOME_DIR, '.config', 'autostart')

ATARASHII_DIR = os.path.join(HOME_DIR, '.atarashii')
CACHE_TIMEOUT = 60 * 60 * 24 * 7 # 7 Days

CONFIG_FILE = os.path.join(ATARASHII_DIR, 'atarashii.conf')
COPY_FILE = '/usr/share/applications/atarashii.desktop'
CRASH_FILE = os.path.join(HOME_DIR, '.atarashii', 'crashed')
CRASH_LOG_FILE = os.path.join(ATARASHII_DIR, 'crash.log')
ERROR_LOG_FILE = os.path.join(ATARASHII_DIR, 'error.log')
LOGOUT_FILE = os.path.join(ATARASHII_DIR, 'logout')

# Theme sounds
from sounds import get_sound_files, get_sound_dirs
THEME_SOUNDS = get_sound_files()
THEME_DIR = get_sound_dirs()[0]


class Settings(object):
    def __init__(self):
        if not os.path.exists(ATARASHII_DIR):
            os.mkdir(ATARASHII_DIR)
        
        # Record running time
        self.values = {}
        self.load()
        self.save_count = 0
        self.has_changed = False
    
    
    # Load ---------------------------------------------------------------------
    def load(self):
        try:
            for line in open(CONFIG_FILE, 'rb'):
                line = line.strip()
                name = line[:line.find(' ')]
                line = line[len(name) + 1:]
                vtype = line[:line.find(' ')]
                value = line[len(vtype) + 1:]
                try:
                    if vtype == 'long':
                        if value == UNSET_SETTING:
                            value = long(UNSET_ID_NUM)
                        
                        else:
                            value = long(value)
                    
                    elif vtype == 'bool':
                        value = True if value == 'True' else False
                    
                    if name != UNSET_SETTING:
                        self.values[urllib.unquote(name)] = value
                
                except ValueError, error:
                    print error
        
        except IOError:
            self.values = {}
        
        # Check crash
        self.check_crash()
        crash_file(False)
    
    
    # Save ---------------------------------------------------------------------
    def save(self):
        if not self.has_changed:
            return
        
        # Don't save crash stuff
        del self['crashed']
        del self['crash_reason']
        
        # Create the file
        with open(CONFIG_FILE, 'wb') as f:
            for key, value in sorted(self.values.items()):
                if isinstance(value, bool):
                    key_type = 'bool'
                
                elif isinstance(value, (int, long)):
                    key_type = 'long'
                
                else:
                    key_type = 'str'
                
                f.write('%s %s %s\n' % (urllib.quote(key), key_type, value))
        
        self.has_changed = False
    
    
    # Get / Set ----------------------------------------------------------------
    def __getitem__(self, key):
        return self.values[key] if key in self.values else None
    
    def __setitem__(self, key, value):
        if not key in self.values or self.values[key] != value:
            self.has_changed = True
            self.values[key] = value
    
    def __delitem__(self, key):
        if key in self.values:
            self.has_changed = True
            del self.values[key]
    
    def isset(self, key, allow_empty=False):
        if self[key] is not None:
            if type(self[key]) == long or type(self[key]) == int:
                return self[key] != -1
            
            elif allow_empty:
                return True
            
            else:
                return self[key].strip() != UNSET_SETTING
    
    def get(self, key, default):
        return self.values.get(key, default)
    
    def is_true(self, key, default=True):
        return default if self[key] is None else self[key]
    
    def get_accounts(self):
        return sorted([i[8:] for i in self.values if i.startswith('account_')])
    
    
    # Manage Autostart ---------------------------------------------------------
    # --------------------------------------------------------------------------
    def set_autostart(self, mode):
        # Create/Delete .desktop file
        try:
            # Try to create the folder if it doesn't exists
            if not os.path.exists(AUTOSTART_DIR):
                os.mkdir(AUTOSTART_DIR)
            
            # Get contents of the desktop file
            with open(COPY_FILE, 'rb') as f:
                text = f.read()
            
            # Tweak the file bit
            bmode = 'true' if mode else 'false'
            text = text.replace('Exec=atarashii', 'Exec=atarashii auto')
            text = text.replace('StartupNotify=true', 'StartupNotify=false')
            with open(DESKTOP_FILE, 'wb') as f:
                f.write(text + '\nX-GNOME-Autostart-enabled=%s' % bmode)
            
            # Only save if we succeeded
            self['autostart'] = mode
        
        except IOError:
            print 'Could not set autostart'
    
    def check_autostart(self):
        if os.path.exists(DESKTOP_FILE):
            try:
                with open(DESKTOP_FILE, 'rb') as f:
                    text = f.read()
                
                if text.find('X-GNOME-Autostart-enabled=false') != -1:
                    self['autostart'] = False
                
                else:
                    self['autostart'] = True
                
            except (OSError, IOError):
                print 'Could not check autostart'
                self['autostart'] = False
        
        else:
            self['autostart'] = False
    
    
    # Crash Handling -----------------------------------------------------------
    # --------------------------------------------------------------------------
    def check_crash(self):
        self['crashed'] = os.path.exists(CRASH_FILE)
        if self['crashed']:
            with open(CRASH_FILE, 'rb') as f:
                self['crash_reason'] = f.read().strip()
            
            print 'ERROR: Atarashii crashed!'
    
    
    # Avatar Cache Handling ----------------------------------------------------
    # --------------------------------------------------------------------------
    def check_cache(self):
        for i in os.listdir(ATARASHII_DIR):
            cache_file = os.path.join(ATARASHII_DIR, i)
            if cache_file[-4:].lower() in ('jpeg', '.jpg', '.png', 'gif'):
                if time.time() - os.stat(cache_file).st_mtime > CACHE_TIMEOUT:
                    try:
                        os.unlink(cache_file)
                    
                    except (OSError, IOError):
                        print 'Could not delete file %s' % cache_file


# Create Crashfile -------------------------------------------------------------
# ------------------------------------------------------------------------------
def crash_file(mode, data=None):
    try:
        if mode:
            with open(CRASH_FILE, 'wb') as f:
                f.write(str(data))
        
        elif os.path.exists(CRASH_FILE):
            os.unlink(CRASH_FILE)
    
    except (OSError, IOError):
        print 'IO on crashfile failed'

