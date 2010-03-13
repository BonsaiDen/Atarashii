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
import sys, os
sys.path.insert(0, os.path.join(sys.path[0], "atarashii/usr/share/pyshared"))
try:
    import atarashii

finally:
    sys.path.pop(0)
    
    
atarashii.debug(sys.path[0])
