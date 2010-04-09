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


# Get files from the current sound theme ---------------------------------------
# ------------------------------------------------------------------------------
import gconf
import os
import threading
import subprocess


def get_sound_theme(theme_name=None):
    if theme_name is None:
        theme_name = gconf.client_get_default().get_string(
                                            '/desktop/gnome/sound/theme_name')
    
    if 'XDG_DATA_DIRS' in os.environ:
        dir_list = os.environ['XDG_DATA_DIRS'].split(':')
    
    else:
        dir_list = []
    
    dir_list.append(os.environ['HOME'] + '/.local/share/')
    
    for i in dir_list:
        i += 'sounds/' + theme_name + '/'
        if os.access(i, os.F_OK):
            return i
    
    return None
    
def get_sound_theme_index(theme_dir):
    index_file = os.path.join(theme_dir, 'index.theme')
    parent = None
    for line in open(index_file):
        line = line.strip()
        if line.startswith('Inherits='):
            parent = line.split('=')[1]
            
        elif line.startswith('Directories='):
            sound_dir = line.split('=')[1].split(',')[0]
    
    return parent, sound_dir

def get_sound_dirs():
    dirs = []

    parent = get_sound_theme()
    count = 0
    while parent:
        par, theme_dir = get_sound_theme_index(parent)
        dirs.append(os.path.join(parent, theme_dir))
           
        if par is not None and count < 20:
            parent = get_sound_theme(par)
            count += 1
        
        else:
            break
    
    return dirs

def get_sound_files():
    sound_files = {}
    for cur_dir in get_sound_dirs():
        files = os.listdir(cur_dir)
        for i in files:
            name, ext = i.lower().split('.')
            if not ext == 'disabled':
                sound_files[name] = os.path.join(cur_dir, i)

    return sound_files


# Sound Player Thread ----------------------------------------------------------
# ------------------------------------------------------------------------------
class Sound(threading.Thread):
    def __init__(self, sound):
        threading.Thread.__init__(self)
        self.daemon = True
        self.sound = sound
        self.start()
    
    def run(self):
        tries = 0
        code = -1
        
        # Wacka! This thing is a mess, sometimes it goes zombie and on other
        # ocasions it just fails. So the kittens just threw some try/except
        # on it!
        player = None
        while code != 0 and tries < 3:
            try:
                # Check for Zombieeeeeees!
                try:
                    if player is not None:
                        player.kill()
                        print 'Sound Zombieeeees!'
                
                except OSError:
                    pass
                
                player = subprocess.Popen(['play', '-q', self.sound])
                code = player.wait()
                if code != 0:
                    print 'sound failed!', code
            
            except OSError, error:
                print 'Failed to play sound', error
            
            tries += 1

