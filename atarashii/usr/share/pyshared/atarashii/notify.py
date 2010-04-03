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
import dbus

import subprocess
import threading

from settings import THEME_SOUNDS


class Notifier:
    def __init__(self, main):
        self.settings = main.settings
        self.last_id = -1
        self.items = []
        
        try:
            bus = dbus.SessionBus()
            self.notify = dbus.Interface(
                               bus.get_object('org.freedesktop.Notifications',
                                              '/org/freedesktop/Notifications'),
                                              'org.freedesktop.Notifications')
            
            self.notify.connect_to_signal("NotificationClosed", self.show)
        
        except dbus.exceptions.DBusException:
            self.notify = None
    
    
    # Try to close the last notification ---------------------------------------
    # This might get ignored on newer version of the notification debus thingy -
    def close(self):
        if self.last_id == -1:
            return
        
        self.notify.CloseNotification(self.last_id)
    
    
    # Add new notifications to the queue ---------------------------------------
    def add(self, items):
        if isinstance(items, tuple):
            items = [items]
        
        if self.notify and self.settings.is_true('notify') \
           and len(items) > 0:
            
            # Add items and save old count
            pending = len(self.items)
            self.items += items
            
            # If there were no pending items show the first new one
            if pending == 0:
                self.last_id = -1
                self.show(-1)
    
    
    # Show a notification ------------------------------------------------------
    def show(self, sid, *args):
        if (sid == -1 or sid == self.last_id) and len(self.items) > 0:
            item = self.items.pop(0)
            self.last_id = self.notify.Notify('Atarashii', 0, item[2],
                                              item[0],  item[1], (),
                                              {'urgency': dbus.Byte(2)},
                                              -1)
            
            # Play the sound
            if self.settings.is_true('sound'):
                if item[3].startswith('theme:'):
                    sound = item[3].split(':')[1]
                    if sound in THEME_SOUNDS:
                        snd = Sound(THEME_SOUNDS[sound])
                        snd.start()
                
                elif self.settings['sound_' + item[3]] not in ('None', ''): 
                    snd = Sound(self.settings['sound_' + item[3]])
                    snd.start()


# Sound Player Thread ----------------------------------------------------------
# ------------------------------------------------------------------------------
class Sound(threading.Thread):
    def __init__(self, sound):
        threading.Thread.__init__(self)
        self.daemon = True
        self.sound = sound
    
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

