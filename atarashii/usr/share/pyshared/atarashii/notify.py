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

from sounds import play_sound
from errors import log_error
from utils import unescape


class Notifier(object):
    def __init__(self, main):
        self.main = main
        self.last_id = -1
        self.items = []
        self.init_dbus()
    
    def init_dbus(self):
        try:
            obj = dbus.SessionBus().get_object('org.freedesktop.Notifications',
                                               '/org/freedesktop/Notifications')
            
            self.notify = dbus.Interface(obj, 'org.freedesktop.Notifications')
            self.notify.connect_to_signal('NotificationClosed', self.show)
        
        except dbus.exceptions.DBusException:
            self.notify = None
    
    
    # Notifications ------------------------------------------------------------
    def add(self, items):
        if isinstance(items, tuple):
            items = [items]
        
        if self.notify and len(items) > 0:
            
            # Add items and save old count
            pending = len(self.items)
            self.items += items
            
            # If there were no pending items show the first new one
            if pending == 0:
                self.last_id = -1
                self.show(-1)
    
    def show(self, item_id, *args):
        if (item_id == -1 or item_id == self.last_id) and len(self.items) > 0:
            item = self.items.pop(0)
            try:
                self.last_id = self.send(item)
            
            # In very strange cases the dbus might go aways while we're running
            # so lets try to grab it again
            except dbus.exceptions.DBusException:
                log_error('DBUS error')
                self.init_dbus()
                self.last_id = self.send(item)
            
            # Play the sound
            play_sound(self.main, item[3])
    
    def send(self, item):
        overlay = self.main.settings.is_true('notify_overlay', True)
        urgent = dbus.Byte(2) if overlay else dbus.Byte(1)
        return self.notify.Notify('Atarashii', 0, item[2], item[0],
                                  unescape(item[1]),
                                  (), {'urgency': urgent}, -1)
    
    # Try to close the last notification, this might get ignored on newer
    # version of the notification dbus thingy
    def close(self):
        if self.last_id == -1:
            return False
        
        try:
            self.notify.CloseNotification(self.last_id)
        
        except dbus.exceptions.DBusException:
            log_error('DBUS error while closing')

