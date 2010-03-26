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
import sys

def get_instance():
    session = dbus.SessionBus()
    obj = session.get_object('org.freedesktop.DBus', '/org/freedesktop/DBus')
    services = dbus.Interface(obj ,'org.freedesktop.DBus').ListNames()
    
    if 'org.bonsaiden.Atarashii' in services:
        sys.exit(69) # os.EX_UNAVAILABLE
    
    else:
        # Needs to be global, if the variable gets gc'ed the dbus instance is
        # automatically removed
        
        return dbus.service.BusName('org.bonsaiden.Atarashii', bus = session)
