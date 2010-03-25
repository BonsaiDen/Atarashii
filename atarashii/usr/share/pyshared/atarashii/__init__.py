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

"""
Atarashii Twitter Client
"""
__version__ = '0.99.16b'
__author__ = 'Ivo Wetzel <ivo.wetzel@googlemail.com>'
__copyright__ = 'Copyright (c) 2010 Ivo Wetzel'
__license__ = 'GPL 3'
__commits__ = '0'
__hash__ = '0000000'

import sys
if sys.path[0] == '/usr/share/pyshared':
    sys.path.pop(0)

def start():
    from atarashii import Atarashii
    Atarashii(__version__).start()

def debug(path):
    from atarashii import Atarashii
    Atarashii(__version__ + '-' + __hash__ + '#' + __commits__, path).start()

def crash(error):
    from settings import crash_file
    crash_file(True, error)

