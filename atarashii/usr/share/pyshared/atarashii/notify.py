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
        self.sound_ids = {}
        self.sounds = []
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
            if self.main.settings.is_true('notify'):
                sound = False
                old_pending = self.pending
                first_sound = None
                while len(self.items) > 0:
                    sound = True
                    item = self.items.pop(0)
                    nid = self.notify.Notify('Atarashii', 0, item[2],
                                                      item[0],  item[1], (),
                                                      {'urgency': dbus.Byte(2)},
                                                      -1)
                    
                    self.sound_ids[nid] = True
                    self.sounds.append(item[3])
                    if first_sound is None:
                        first_sound = item[3]
                    
                    self.pending += 1
                
                if sound and old_pending == 0:
                    self.first_shown = False
                    self.play_sound(-1, sound = first_sound)
                
            time.sleep(0.1)
    
    # Play the sound using mplayer ---------------------------------------------
    def play_sound(self, sid, sound=None):
        # Fix for the initial notification
        if sid == -1:
            sound = self.get_sound(sound)
            if sound is None:
                return  
        
        # Make sure we've created the notification we want a sound be played for
        elif self.sound_ids.has_key(sid):
            del self.sound_ids[sid]
            
            self.pending -= 1
            if self.pending == 0:
                self.last_id = -1
                return
            
            sound = self.get_sound(self.sounds.pop(0))
            if sound is None:
                return
        
        else:
            return
        
        # Play the sound
        Sound(sound)
        
    def get_sound(self, snd):
        if self.main.settings.is_true('sound') \
           and self.main.settings['sound_' + snd] != 'None':
            return self.main.settings['sound_' + snd]
        
        else:
            return None



class Sound(threading.Thread):
    def __init__(self,sound):
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

