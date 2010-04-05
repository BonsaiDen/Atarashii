#!/usr/bin/python

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


# Debug Mode Started -----------------------------------------------------------
# ------------------------------------------------------------------------------
import sys
import os

PATH = os.path.join(sys.path[0], 'atarashii/usr/share/pyshared')


# Import Atarashii -------------------------------------------------------------
try:
    sys.path.insert(0, PATH)
    import atarashii
    sys.path.pop(0)
    
except:
    if sys.path[0] == PATH:
        sys.path.pop(0)
    
    exit(75)
    
# Start Atarashii
atarashii.debug(sys.path[0])
exit(0)

