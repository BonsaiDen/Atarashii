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


# DBUS Integration -------------------------------------------------------------
# ------------------------------------------------------------------------------
import dbus
import dbus.service
import gobject

from constants import DESK_NAME, DESK_PATH, DBUS_NAME, DBUS_PATH

from dbus.mainloop.glib import DBusGMainLoop
DBusGMainLoop(set_as_default = True)


class AtarashiiObject(dbus.service.Object):
    def __init__(self):
        self.main = None
        self.is_unique = False
        
        self.session = dbus.SessionBus()
        self.obj = self.session.get_object(DESK_NAME, DESK_PATH)
        services = dbus.Interface(self.obj, DESK_NAME).ListNames()
        
        # Is Atarashii already running?
        if DBUS_NAME in services:
            obj = self.session.get_object(DBUS_NAME, DBUS_PATH)
            atarashii = dbus.Interface(obj, DBUS_NAME)
            
            # Show the window
            atarashii.present()
        
        else:
            self.is_unique = True
            bus_name = dbus.service.BusName(DBUS_NAME, bus = self.session)
            dbus.service.Object.__init__(self, bus_name, DBUS_PATH)
    
    def set_main(self, main):
        self.main = main
    
    # DBUS interface -----------------------------------------------------------
    @dbus.service.method(DBUS_NAME)
    def present(self):
        if self.main is not None:
            gobject.idle_add(self.main.gui.force_present)

