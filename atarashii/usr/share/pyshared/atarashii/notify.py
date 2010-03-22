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
import pynotify
import subprocess
import threading


# Wacka! This thing is one more mess, sometimes it goes zombie and on other
# ocasions it just failes. So the kittens just throw some try/except onto it!
class Sound(threading.Thread):
    def __init__(self, parent, snd_file):
        threading.Thread.__init__(self)
        self.snd_file = snd_file
        self.parent = parent
    
    def run(self):
        tries = 0
        code = -1
        while code != 0 and tries < 3:
            try:
                # Check for Zombieeeeeees!
                try:
                    if self.parent.player != None:
                        self.parent.player.kill()
                        print 'Zombieeeees!'
                
                except OSError:
                    pass
                
                self.parent.player = subprocess.Popen(
                                                ['mplayer', '-really-quiet',
                                                 '-nolirc', self.snd_file])
                
                code = self.parent.player.wait()
                if code != 0:
                    print 'sound failed!', code
            
            except OSError, error:
                print 'Failed to play sound', error
        
            tries += 1

class Notifier:
    def __init__(self, main):
        self.main = main
        self.player = None
        
    def show(self, objs):
        if len(objs) > 0 and self.main.settings.is_true('sound') \
           and self.main.settings['soundfile'] != 'None':
            snd = Sound(self, self.main.settings['soundfile'])
            snd.setDaemon(True)
            snd.start()
        
        # Shot notification
        for obj in objs:
            try:
                pynotify.Notification(obj[0], obj[1], obj[2]).show()
                            
            except Exception, error:
                print 'Notify error', error


def init():
    pynotify.init('Atarashii')

def uninit():
    pynotify.uninit()

