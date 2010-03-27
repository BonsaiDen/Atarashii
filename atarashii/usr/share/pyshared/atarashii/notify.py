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


class Notifier(threading.Thread):
    def __init__(self, main):
        threading.Thread.__init__(self)
        self.main = main
        self.items = []
        self.player = None
        self.sound_types = {}
        self.last_id = -1
        self.pending = 0
        
        try:
            bus = dbus.SessionBus()
            self.notify = dbus.Interface(
                               bus.get_object('org.freedesktop.Notifications',
                                              '/org/freedesktop/Notifications'),
                                              'org.freedesktop.Notifications')
            
            self.notify.connect_to_signal("NotificationClosed", self.play_sound)
        
        except dbus.exceptions.DBusException:
            self.notify = None
            
        self.daemon = True
        self.start()
    
    def run(self):
        if not self.notify:
            return
        
        while True:
            sound = False
            old_pending = self.pending
            while len(self.items) > 0:
                sound = True
                item = self.items.pop(0)
                snd_type = item[3]
                self.sound_types[self.last_id] = snd_type
                self.pending += 1
                self.last_id = self.notify.Notify('Atarashii', 0, item[2], item[0],
                                            item[1], (),
                                            {'urgency': dbus.Byte(2) }, -1)
            
            if sound and old_pending == 0:                
                self.play_sound(-1)
            
            time.sleep(0.1)
    
    # Play the sound using mplayer ---------------------------------------------
    def play_sound(self, sid, *args):
                
        # Make sure we've created the notification we want a sound be played for
        if self.sound_types.has_key(sid):
            self.pending -= 1
            if self.pending == 0:
                self.last_id = -1
            
            print "pending", self.pending
            sound = self.get_sound(self.sound_types[sid])
            del self.sound_types[sid]
            if sound is None:
                return
        
        else:
            return
        
        tries = 0
        code = -1
        
        # Wacka! This thing is a mess, sometimes it goes zombie and on other
        # ocasions it just fails. So the kittens just threw some try/except 
        # on it!
        while code != 0 and tries < 3:
            try:
                # Check for Zombieeeeeees!
                try:
                    if self.player is not None:
                        self.player.kill()
                        print 'Sound Zombieeeees!'
                
                except OSError:
                    pass
                
                self.player = subprocess.Popen(['play', '-q', sound])
                code = self.player.wait()
                if code != 0:
                    print 'sound failed!', code
                
                else:
                    self.player = None
            
            except OSError, error:
                print 'Failed to play sound', error
            
            tries += 1
    
    def get_sound(self, snd):
        if self.main.settings.is_true('sound') \
           and self.main.settings['sound_' + snd] != 'None':
            return self.main.settings['sound_' + snd]
        
        else:
            return None

