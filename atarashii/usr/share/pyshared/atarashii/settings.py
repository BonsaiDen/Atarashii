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
DESKTOP_FILE = os.path.join(os.path.expanduser('~'), '.config',
                            'autostart', 'atarashii.desktop')

COPY_FILE = '/usr/share/applications/atarashii.desktop'
CRASH_FILE = os.path.join(os.path.expanduser('~'), '.atarashii', 'crashed')


class Settings:
    def __init__(self):
        self.dir = os.path.join(os.path.expanduser('~'), ".atarashii")
        if not os.path.exists(self.dir):
            os.mkdir(self.dir)
        
        # Record running time
        self.init_time = time.time()        
        self.values = {}
        self.load()
        
    
    # Load ---------------------------------------------------------------------
    def load(self):
        try:
            settings_file = open(os.path.join(self.dir, 'atarashii.conf'), "r")
            lines = settings_file.read().split('\n')
            settings_file.close()
            for i in lines:
                name = i[:i.find(' ')]
                i = i[len(name)+1:]
                vtype = i[:i.find(' ')]
                value = i[len(vtype)+1:]
                try:
                    if vtype == 'long':
                        if value == "":
                            value = long(-1)
                        
                        else:
                            value = long(value)
                    
                    elif vtype == 'bool':
                        value = True if value == "True" else False
                    
                    if name != "":
                        self.values[urllib.unquote(name)] = value
                
                except ValueError, detail:
                    print detail
        
        except IOError:
            self.values = {}
    
        # Check autostart
        self.check_autostart()
        
        # Check crash
        self.check_crash()
        self.crash_file(True)
    
    
    # Save ---------------------------------------------------------------------
    def save(self):
        # Don't save crash stuff
        if self.values.has_key("crashed"):
            del self.values['crashed']
        
        if self.values.has_key("time_before_crash"):
            del self.values['time_before_crash']         
        
        # Test
        settings_file = open(os.path.join(self.dir, 'atarashii.conf'), "w")
        keys = self.values.keys()
        keys.sort()
        for name in keys:
            value = self.values[name]
            cls = type(value)
            if cls == int or cls == long:
                vtype = "long"
            
            elif cls == bool:
                vtype = "bool"
            
            else:
                vtype = "str"
            
            settings_file.write("%s %s %s\n" % (urllib.quote(name), vtype,
                                value))
        
        settings_file.close()
    
    
    # Get / Set ----------------------------------------------------------------
    def __getitem__(self, key):
        if self.values.has_key(key):
            return self.values[key]
        else:
            return None
    
    def __setitem__(self, key, value):
        self.values[key] = value
    
    def __delitem__(self, key):
        if self.values.has_key(key):
            del self.values[key]
    
    def isset(self, key):
        if self[key] != None:
            if type(self[key]) == long or type(self[key]) == int:
                return self[key] != -1
            else:
                return self[key].strip() != ""
    
    def is_true(self, key, default = True):
        if self[key] == None:
            return default
        
        else:
            return self[key]
    
    def get_accounts(self):
        accounts = []
        for i in self.values.keys():
            if i.startswith("account_"):
                accounts.append(i[8:])
        
        accounts.sort()
        return accounts


    # Manage Autostart ---------------------------------------------------------
    # --------------------------------------------------------------------------
    def set_autostart(self, mode):
        # Do nothing
        if mode == self['autostart']:
            return
           
        # Create/Delete .desktop file
        try:
            cfp = open(COPY_FILE, "rb")
            text = cfp.read()
            cfp.close()
            
            dfp = open(DESKTOP_FILE, "wb")
            bmode = "true" if mode else "false"
            text = text.replace("Exec=atarashii", "Exec=atarashii &")
            dfp.write(text + "\nX-GNOME-Autostart-enabled=%s" % bmode)
            dfp.close()
            
            # Only save if we succeeded
            self['autostart'] = mode
        
        except IOError:
            print "Could not set autostart"
    
    def check_autostart(self):
        self['autostart'] = os.path.exists(DESKTOP_FILE)
        
        
    # Crash Handling -----------------------------------------------------------
    # --------------------------------------------------------------------------
    def check_crash(self):
        self['crashed'] = os.path.exists(CRASH_FILE)
        if self['crashed']:
            cfp = open(CRASH_FILE, "rb")
            self['time_before_crash'] = int(cfp.read())
            cfp.close()
            
            print "ERROR: Atarashii crashed!"
            print "Runtime before crash %2.2f minutes" % \
                   (self['time_before_crash'] / 60.0)
    
    def crash_file(self, mode):
        try:
            if mode:
                cfp = open(CRASH_FILE, "wb")
                cfp.write(str(int(time.time() - self.init_time)))
                cfp.close()
                
            else:
                os.unlink(CRASH_FILE)
        
        except IOError:
            print "IO on crashfile failed"

