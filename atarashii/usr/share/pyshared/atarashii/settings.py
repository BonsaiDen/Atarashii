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

# File Paths
HOME_DIR = os.path.expanduser('~')
DESKTOP_FILE = os.path.join(HOME_DIR, '.config',
                            'autostart', 'atarashii.desktop')

AUTOSTART_DIR = os.path.join(HOME_DIR, '.config', 'autostart')

ATARASHII_DIR = os.path.join(HOME_DIR, '.atarashii')
CACHE_TIMEOUT = 60 * 60 * 24 * 7 # 7 Days

COPY_FILE = '/usr/share/applications/atarashii.desktop'
CRASH_FILE = os.path.join(HOME_DIR, '.atarashii', 'crashed')
CRASH_LOG_FILE = os.path.join(ATARASHII_DIR, 'crash.log')
LOGOUT_FILE = os.path.join(ATARASHII_DIR, 'logout')


class Settings:
    def __init__(self):
        if not os.path.exists(ATARASHII_DIR):
            os.mkdir(ATARASHII_DIR )
        
        # Record running time
        self.values = {}
        self.load()
        self.save_count = 0
        self.has_changed = False
        
    
    # Load ---------------------------------------------------------------------
    def load(self):
        try:
            settings_file = open(os.path.join(ATARASHII_DIR,
                                 'atarashii.conf'), 'r')
            
            lines = settings_file.read().split('\n')
            settings_file.close()
            for i in lines:
                name = i[:i.find(' ')]
                i = i[len(name)+1:]
                vtype = i[:i.find(' ')]
                value = i[len(vtype)+1:]
                try:
                    if vtype == 'long':
                        if value == '':
                            value = long(-1)
                        
                        else:
                            value = long(value)
                    
                    elif vtype == 'bool':
                        value = True if value == 'True' else False
                    
                    if name != '':
                        self.values[urllib.unquote(name)] = value
                
                except ValueError, detail:
                    print detail
        
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
        if self.values.has_key('crashed'):
            del self.values['crashed']
        
        if self.values.has_key('crash_reason'):
            del self.values['crash_reason']
        
           
        # Test
        settings_file = open(os.path.join(ATARASHII_DIR, 'atarashii.conf'), 'w')
        keys = self.values.keys()
        keys.sort()
        for name in keys:
            value = self.values[name]
            cls = type(value)
            if cls == int or cls == long:
                vtype = 'long'
            
            elif cls == bool:
                vtype = 'bool'
            
            else:
                vtype = 'str'
            
            settings_file.write('%s %s %s\n'
                                 % (urllib.quote(name), vtype, value))
        
        settings_file.close()
        self.has_changed = False
    
    
    # Get / Set ----------------------------------------------------------------
    def __getitem__(self, key):
        if self.values.has_key(key):
            return self.values[key]
        else:
            return None
    
    def __setitem__(self, key, value):
        if not self.values.has_key(key) or self.values[key] != value:
            self.has_changed = True
            self.values[key] = value
    
    def __delitem__(self, key):
        if self.values.has_key(key):
            self.has_changed = True
            del self.values[key]
    
    def isset(self, key):
        if self[key] is not None:
            if type(self[key]) == long or type(self[key]) == int:
                return self[key] != -1
            
            else:
                return self[key].strip() != ''
    
    def is_true(self, key, default=True):
        if self[key] is None:
            return default
        
        else:
            return self[key]
    
    def get_accounts(self):
        accounts = []
        for i in self.values.keys():
            if i.startswith('account_'):
                accounts.append(i[8:])
        
        accounts.sort()
        return accounts
    
    
    # Manage Autostart ---------------------------------------------------------
    # --------------------------------------------------------------------------
    def set_autostart(self, mode):
        # Create/Delete .desktop file
        try:
            # Try to create the folder if it doesn't exists
            if not os.path.exists(AUTOSTART_DIR):
                os.mkdir(AUTOSTART_DIR)
            
            # Get contents of the desktop file
            cfp = open(COPY_FILE, 'rb')
            text = cfp.read()
            cfp.close()
            
            # Tweak the file bit
            dfp = open(DESKTOP_FILE, 'wb')
            bmode = 'true' if mode else 'false'
            text = text.replace('Exec=atarashii', 'Exec=atarashii auto')
            text = text.replace('StartupNotify=true', 'StartupNotify=false')
            dfp.write(text + '\nX-GNOME-Autostart-enabled=%s' % bmode)
            dfp.close()
            
            # Only save if we succeeded
            self['autostart'] = mode
        
        except IOError:
            print 'Could not set autostart'
    
    def check_autostart(self):
        if os.path.exists(DESKTOP_FILE):
            try:
                cfp = open(DESKTOP_FILE, 'rb')
                text = cfp.read()
                cfp.close()
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
            cfp = open(CRASH_FILE, 'rb')
            self['crash_reason'] = cfp.read().strip()
            cfp.close()
            print 'ERROR: Atarashii crashed!'
    
    
    # Avatar Cache Handling ----------------------------------------------------
    # --------------------------------------------------------------------------
    def check_cache(self):
        for i in os.listdir(ATARASHII_DIR):
            cache_file = os.path.join(ATARASHII_DIR, i)
            
            # TODO determin wether to check for last access or last modification
            if time.time() - os.stat(cache_file).st_atime > CACHE_TIMEOUT:
                if cache_file[-4:].lower() in ('jpeg', '.jpg', '.png', 'gif'):
                    try:
                        os.unlink(cache_file)
                    
                    except (OSError, IOError):
                        print 'Could not delete file %s' % i


# Create Crashfile -------------------------------------------------------------
# ------------------------------------------------------------------------------
def crash_file(mode, data=None):
    try:
        if mode:
            cfp = open(CRASH_FILE, 'wb')
            cfp.write(str(data))
            cfp.close()
        
        elif os.path.exists(CRASH_FILE):
            os.unlink(CRASH_FILE)
    
    except (OSError, IOError):
        print 'IO on crashfile failed'

