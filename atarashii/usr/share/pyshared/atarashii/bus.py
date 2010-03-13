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

if 'org.Atarashii' in dbus.Interface(
    dbus.SessionBus().get_object(
        "org.freedesktop.DBus", "/org/freedesktop/DBus"),
        "org.freedesktop.DBus").ListNames():
    
    sys.exit(2)
    
DBUS = dbus.SessionBus()
DBUSNAME = dbus.service.BusName('org.Atarashii', bus = DBUS)

