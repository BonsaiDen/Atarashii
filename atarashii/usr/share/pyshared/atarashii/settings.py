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

# File Paths
DESKTOP_FILE = os.path.join(os.path.expanduser('~'), '.config',
                            'autostart', 'atarashii.desktop')

COPY_FILE = '/usr/share/applications/atarashii.desktop'

class Settings:
    def __init__(self):
        self.dir = os.path.join(os.path.expanduser('~'), ".atarashii")
        if not os.path.exists(self.dir):
            os.mkdir(self.dir)
        
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
                
                except Exception, detail:
                    print detail
        
        except Exception, detail:
            self.values = {}
    
        # Check autostart
        self.check_autostart()
    
    
    # Save ---------------------------------------------------------------------
    def save(self):
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
            if mode:
                cfp = open(COPY_FILE, "rb")
                text = cfp.read()
                cfp.close()
                
                dfp = open(DESKTOP_FILE, "wb")
                dfp.write(text)
                dfp.close()
                
            else:
                os.unlink(DESKTOP_FILE)
            
            # Only save if we succeeded
            self['autostart'] = mode
        
        except:
            print "Could not set autostart"
    
    def check_autostart(self):
        self['autostart'] = os.path.exists(DESKTOP_FILE)
    
