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


# Language loader --------------------------------------------------------------
# ------------------------------------------------------------------------------
import locale
import sys
import os


class Language(object):
    def __init__(self):
        try:
            self.code = sys.argv[sys.argv.index('-l') + 1]
        
        except ValueError:
            self.code = locale.getdefaultlocale()[0][0:2]
        
        try:
            sys.path.insert(0, os.path.dirname(__file__))
            lang = self.get_lang()
        
        finally:
            sys.path.pop(0)
        
        for key, value in lang.LANG.iteritems():
            setattr(self, key, value)
    
    def name(self, text):
        if text[-1] in 'xzs':
            return text + self.name_end_xzs
        
        else:
            return text + self.name_end
    
    def get_lang(self):
        for i in os.listdir(os.path.dirname(__file__)):
            if i == 'lang_%s.py' % self.code:
                return __import__('lang_%s' % self.code)
        
        
        return __import__('lang_en')

LANG = Language()

