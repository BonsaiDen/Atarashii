#  This file is part of  Atarashii.
#
#   Atarashii is free software: you can redistribute it and/or 
#  modify it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#   Atarashii is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
# 
#  You should have received a copy of the GNU General Public License along with
#  Atarashii. If not, see <http://www.gnu.org/licenses/>.


# Text Input -------------------------------------------------------------------
# ------------------------------------------------------------------------------
import pygtk
pygtk.require('2.0')
import gtk
import gobject

class TextInput(gtk.TextView):
	__gsignals__ = {
		"submit": (gobject.SIGNAL_RUN_LAST | gobject.SIGNAL_ACTION, None, ())
	}

	def __init__(self):
		gtk.TextView.__init__(self)
		self.set_border_width(0)
		self.set_wrap_mode(gtk.WRAP_WORD_CHAR)
		self.set_pixels_above_lines(2)
		self.set_pixels_below_lines(2)
		self.set_left_margin(2)
		self.set_right_margin(2)
		self.set_accepts_tab(True)
		self.set_editable(True)
		self.set_cursor_visible(True)
		
		self.base_color = self.get_style().base[gtk.STATE_NORMAL]
	#	self.error_color = gtk.gdk.color_parse("indianred")

gtk.binding_entry_add_signal(TextInput, gtk.keysyms.Return, 0, "submit")
gtk.binding_entry_add_signal(TextInput, gtk.keysyms.KP_Enter, 0, "submit")


