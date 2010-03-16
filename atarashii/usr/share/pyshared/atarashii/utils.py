#  This file is part of Atarashii.
#
#  Atarashii is free software: you can redistribute it and/or
#  modify it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Atarashii is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License along with
#  Atarashii. If not, see <http://www.gnu.org/licenses/>.


# Utility stuff ----------------------------------------------------------------
# ------------------------------------------------------------------------------
ENTITIES = {
    "&": "&amp;",
    '"': "&quot;",
    "'": "&apos;",
    ">": "&gt;",
    "<": "&lt;"
}

def escape(text):
    return "".join(ENTITIES.get(c, c) for c in text)

def unescape(text):
    for key, value in ENTITIES.iteritems():
        text = text.replace(value, key)
    
    return text

def compare(item_x, item_y):
    if item_x.id > item_y.id:
        return -1
    
    elif item_x.id < item_y.id:
        return 1
    
    else:
        return 0
        
def compare_sub(item_x, item_y):
    if item_x[0].id > item_y[0].id:
        return 1
    
    elif item_x[0].id < item_y[0].id:
        return -1
    
    else:
        return 0
        

