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
import dbus


# Wacka! This thing is one more mess, sometimes it goes zombie and on other
# ocasions it just failes. So the kittens just throw some try/except onto it!
class Notifier(threading.Thread):
    def __init__(self, main):
        threading.Thread.__init__(self)
        self.main = main
        self.items = []
        self.player = None
        try:
            bus = dbus.SessionBus()
            self.notify = dbus.Interface(
                               bus.get_object('org.freedesktop.Notifications',
                                              '/org/freedesktop/Notifications'),
                                              'org.freedesktop.Notifications')  
        
        except dbus.exceptions.DBusException:
            self.notify = None
            
        self.daemon = True
        self.start()
    
    def run(self):
        if not self.notify:
            return
        
        while True:
            sound = False
            while len(self.items) > 0:
                sound = True
                item = self.items.pop(0)
                self.notify.Notify('Atarashii', 0, item[2], item[0], item[1],
                                   (),{'urgency': dbus.Byte(2) }, -1)
            
            if sound and self.get_sound():
                self.play_sound()
            
            time.sleep(0.1)
    
    # Play the sound using mplayer ---------------------------------------------
    def play_sound(self):
        tries = 0
        code = -1
        while code != 0 and tries < 3:
            try:
                # Check for Zombieeeeeees!
                try:
                    if self.player is not None:
                        self.player.kill()
                        print 'Sound Zombieeeees!'
                
                except OSError:
                    pass
                
                self.player = subprocess.Popen(['play', '-q', self.get_sound()])
                
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

