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


# Notifications ----------------------------------------------------------------
# ------------------------------------------------------------------------------
import subprocess
import threading
import time

from utils import escape

# Wacka! This thing is one more mess, sometimes it goes zombie and on other
# ocasions it just failes. So the kittens just throw some try/except onto it!
class Notifier(threading.Thread):
    def __init__(self, main):
        threading.Thread.__init__(self)
        self.main = main
        self.items = []
        self.player = None
        self.notify = None
    
    def run(self):
        while True:
            sound = False
            while len(self.items) > 0:
                sound = True
                item = self.items.pop(0)
                self.show_notify(item)
                
            if sound and self.get_sound():
                self.play_sound()
            
            time.sleep(0.1)
    
    
    # Show a notification ------------------------------------------------------
    def show_notify(self, item):
        tries = 0
        code = -1
        while code != 0 and tries < 3:
            try:
                # Check for Zombieeeeeees!
                try:
                    if self.notify != None:
                        self.notify.kill()
                        print 'Notify Zombieeeees!'
                
                except OSError:
                    pass
                
                self.notify = subprocess.Popen(
                                         ['notify-send', '-i',
                                          '%s' % item[2],
                                          '%s' % escape(item[0]),
                                          '%s' % escape(item[1])])
                
                code = self.notify.wait()
                if code != 0:
                    print ' notification failed!', code
            
            except OSError, error:
                print 'Failed to show notification', error
            
            tries += 1  
    
    
    # Play the sound using mplayer ---------------------------------------------
    def play_sound(self):
        tries = 0
        code = -1
        while code != 0 and tries < 3:
            try:
                # Check for Zombieeeeeees!
                try:
                    if self.player != None:
                        self.player.kill()
                        print 'Sound Zombieeeees!'
                
                except OSError:
                    pass
                
                self.player = subprocess.Popen(
                                         ['mplayer', '-really-quiet',
                                          '-nolirc', self.get_sound()])
                
                code = self.player.wait()
                if code != 0:
                    print 'sound failed!', code
            
            except OSError, error:
                print 'Failed to play sound', error
            
            tries += 1
    
    def get_sound(self):
        if self.main.settings.is_true('sound') \
           and self.main.settings['soundfile'] != 'None':
            return self.main.settings['soundfile']
        
        else:
            return None

