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
import json

from errors import log_error, crash_file

from constants import UNSET_SETTING, UNSET_ID_NUM, FONT_DEFAULT, \
                      AVATAR_DEFAULT, THEME_DEFAULT

from constants import ATARASHII_DIR, CACHE_DIR, CONFIG_FILE, CRASH_FILE, \
                      DESKTOP_FILE, CACHE_TIMEOUT, AUTOSTART_DIR, COPY_FILE, \
                      USERLIST_FILE


class Settings(object):
    def __init__(self, main):
        if not os.path.exists(ATARASHII_DIR):
            os.mkdir(ATARASHII_DIR)
        
        if not os.path.exists(CACHE_DIR):
            os.mkdir(CACHE_DIR)
        
        self.main = main
        self.values = {}
        self.user_list = []
        self.user_list_lower = []
        self.removed_list = []
        self.load()
        self.save_count = 0
        self.users_changed = False
        self.users_unsorted = False
        self.has_changed = False
        
        # Theme and CSS
        self.color_themes = {}
        self.load_color_themes()
        self.css_file = None
        self.css_count = 0
        self.css()
    
    
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
                    log_error('%s' % error)
        
        except IOError:
            self.values = {}
        
        # Users
        try:
            with open(USERLIST_FILE, 'rb') as f:
                users = f.read().split(',')
                self.user_list = [i.strip() for i in users if i.strip() != '']
                self.users_unsorted = True
                self.sort_users()
        
        except IOError:
            self.user_list = []
        
        # Check crash
        self.check_crash()
        crash_file(False)
    
    
    # Save ---------------------------------------------------------------------
    def save(self):
        if self.users_changed:
            with open(USERLIST_FILE, 'wb') as f:
                f.write(','.join(self.user_list))
            
            self.users_changed = False
        
        if not self.has_changed:
            return False
        
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
    
    
    # Usernames ----------------------------------------------------------------
    def add_users(self, users):
        for i in users:
            self.add_username(i.screen_name)
        
        self.sort_users()
    
    def add_user(self, item):
        if hasattr(item, 'user'):
            self.add_username(item.user.screen_name)
            
            if hasattr(item, 'retweeted_status'):
                self.add_username(item.retweeted_status.user.screen_name)
            
            if item.in_reply_to_screen_name:
                self.add_username(item.in_reply_to_screen_name)
        
        elif hasattr(item, 'sender'):
            self.add_username(item.sender.screen_name)
        
        if hasattr(item, 'recipient'):
            self.add_username(item.recipient.screen_name)
    
    def add_username(self, name, follow=False):
        name_lower = name.lower()
        if follow and name_lower in self.removed_list:
            self.removed_list.remove(name_lower)
        
        if not name_lower in self.removed_list:
            if not name_lower in self.user_list_lower:
                self.user_list.append(name)
                self.user_list_lower.append(name.lower())
                self.users_unsorted = True
            
            # Replace users when they have changed their casing
            else:
                index = self.user_list_lower.index(name_lower)
                if self.user_list[index] != name:
                    self.user_list[index] = name
                    self.users_unsorted = True
    
    def remove_username(self, name):
        name_lower = name.lower()
        if name_lower in self.user_list_lower:
            for i, user in enumerate(self.user_list):
                if name_lower == user.lower():
                    self.user_list_lower.pop(i)
                    self.user_list.pop(i)
                    self.removed_list.append(name_lower)
                    self.users_changed = True
                    break
    
    def sort_users(self):
        if not self.users_unsorted:
            return False
        
        self.users_changed = True
        self.users_unsorted = False
        users = self.user_list[:]
        self.user_list = []
        self.user_list_lower = []
        
        # Sort aplhabetically and by length
        for item in sorted([(i, len(i)) for i in users]):
            user_lower = item[0].lower()
            if not user_lower in self.user_list_lower:
                self.user_list.append(item[0])
                self.user_list_lower.append(user_lower)
    
    # Return the correct capitalization for a username if it's in the userlist
    def get_username(self, name):
        if name.lower() in self.user_list_lower:
            name = self.user_list[self.user_list_lower.index(name.lower())]
        
        return name
    
    
    # CSS ----------------------------------------------------------------------
    def css(self, font=None, avatar=None, color_theme=None):
        # Delete old css files
        for i in os.listdir(ATARASHII_DIR):
            css_file = os.path.join(ATARASHII_DIR, i)
            if css_file.lower().endswith('.css'):
                os.unlink(css_file)
        
        self.css_file = os.path.join(ATARASHII_DIR,
                                     'atarashii_%s.css' % self.css_count)
        
        self.css_count += 1
        
        # Avatar / Font
        avatar_size = avatar if avatar is not None \
                             else self.get('avatarsize', AVATAR_DEFAULT)
        
        font_size = font if font is not None \
                         else self.get('fontsize', FONT_DEFAULT)
        
        # Theme
        if color_theme is not None:
            self.load_color_themes()
        
        if not self['color_theme'] in self.color_themes:
            self['color_theme'] = THEME_DEFAULT
        
        if color_theme is None:
            color_theme = self['color_theme']
        
        with open(self.main.get_resource('atarashii.css'), 'rb') as f:
            css_data = f.read()
            with open(self.css_file, 'wb') as csf:
                csf.write('/* THIS FILE HAS BEEN AUTOMATICALLY GENERATED '
                         'AND WILL BE OVERRIDEN */\n\n')
                
                path = os.path.join(self.main.get_resource(''), 'themes',
                                    color_theme) + '/'
                
                css_data = css_data.replace('{RESOURCES}', path)
                
                css_data = css_data.replace('{AVATAR32}', str(avatar_size))
                css_data = css_data.replace('{AVATAR34}', str(avatar_size + 2))
                css_data = css_data.replace('{AVATAR38}', str(avatar_size + 6))
                css_data = css_data.replace('{AVATAR48}', str(avatar_size + 16))
                css_data = css_data.replace('{AVATAR54}', str(avatar_size + 22))
                
                css_data = css_data.replace('{FONT9}', str(font_size - 1))
                css_data = css_data.replace('{FONT10}', str(font_size))
                css_data = css_data.replace('{FONT11}', str(font_size + 1))
                css_data = css_data.replace('{FONT12}', str(font_size + 2))
                css_data = css_data.replace('{FONT13}', str(font_size + 3))
                css_data = css_data.replace('{FONT14}', str(font_size + 4))
                
                colors = self.color_themes[color_theme]['colors']
                for key, value in colors.iteritems():
                    css_data = css_data.replace('{%s}' % key, value)
                
                csf.write(css_data)
    
    
    # Load themes --------------------------------------------------------------
    def load_color_themes(self):
        self.color_themes = {}
        self.scan_theme_folder(os.path.join(self.main.get_resource(''),
                                            'themes'))
        
        self.scan_theme_folder(os.path.join(ATARASHII_DIR,'themes'))
    
    def scan_theme_folder(self, path):
        if not os.path.exists(path):
            return False
        
        for theme_name in sorted(os.listdir(path)):
            theme = os.path.join(path, theme_name)
            if os.path.isdir(theme):
                theme_file = os.path.join(theme, 'theme.py')
                if os.path.exists(theme_file):
                    self.read_theme(theme_name, theme_file)
    
    def read_theme(self, name, theme_file):
        with open(theme_file, 'rb') as f:
            lines = [e.strip() for e in f if not e.strip().startswith('#')]
            try:
                self.color_themes[name] = json.loads(
                                          ''.join(lines).replace('\'', '"'))
            
            except (TypeError, ValueError):
                log_error('Invalid theme description for "%s"' % name)
    
    
    # Manage Autostart ---------------------------------------------------------
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
            log_error('Could not set autostart')
    
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
                log_error('Could not check autostart')
                self['autostart'] = False
        
        else:
            self['autostart'] = False
    
    
    # Crash Handling -----------------------------------------------------------
    def check_crash(self):
        self['crashed'] = os.path.exists(CRASH_FILE)
        if self['crashed']:
            with open(CRASH_FILE, 'rb') as f:
                self['crash_reason'] = f.read().strip()
            
            log_error('Atarashii crashed')
    
    
    # Avatar Cache Handling ----------------------------------------------------
    def check_cache(self):
        for i in os.listdir(CACHE_DIR):
            cache_file = os.path.join(CACHE_DIR, i)
            if cache_file[-4:].lower() in ('jpeg', '.jpg', '.png', '.gif'):
                if time.time() - os.stat(cache_file).st_mtime > CACHE_TIMEOUT:
                    try:
                        os.unlink(cache_file)
                    
                    except (OSError, IOError):
                        log_error('Could not delete file %s' % cache_file)

