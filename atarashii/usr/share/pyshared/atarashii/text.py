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


# GUI --------------------------------------------------------------------------
# ------------------------------------------------------------------------------
import pygtk
pygtk.require('2.0')
import gtk
import gtk.glade
import gobject
import pango

import re

from lang import lang

class TextInput(gtk.TextView):
	__gsignals__ = {
		"submit": (gobject.SIGNAL_RUN_LAST | gobject.SIGNAL_ACTION, None, ())
	}

	def __init__(self, gui):
		gtk.TextView.__init__(self)
		self.gui = gui
		self.main = gui.main
		
		# Variables
		self.typing = False
		self.hasFocus = False
		self.isTyping = False
		self.hasTyped = False
		self.isChanging = False
		self.replyRegex = re.compile('@([^\s]+)\s.*')
		
		# Sizes
		self.inputSize = None
		self.inputError = None
		
		# Colors
		self.defaultBG = self.get_style().base[gtk.STATE_NORMAL]
		self.defaultFG = self.get_style().text[gtk.STATE_NORMAL]
		
		# Setup
		self.set_border_width(0)
		self.set_wrap_mode(gtk.WRAP_WORD_CHAR)
		self.set_pixels_above_lines(2)
		self.set_pixels_below_lines(2)
		self.set_left_margin(2)
		self.set_right_margin(2)
		self.set_accepts_tab(True)
		self.set_editable(True)
		self.set_cursor_visible(True)
		
		# Events
		self.connect("submit", self.submit)
		self.get_buffer().connect("changed", self.changed)
		self.connect("focus-in-event", self.focus)
	
	
	# Focus Events -------------------------------------------------------------
	# --------------------------------------------------------------------------
	def focus(self, *args):
		self.hasFocus = True
		self.resize()
		if not self.hasTyped:
			self.modify_text(gtk.STATE_NORMAL, self.defaultFG)
			self.get_buffer().set_text("")
	
	
	def looseFocus(self):
		if not self.hasFocus:
			self.resize()
			if not self.hasTyped:
				self.modify_text(gtk.STATE_NORMAL, self.get_style().text[gtk.STATE_INSENSITIVE])
				self.get_buffer().set_text(lang.textEntry)
		
		return False
	
	def htmlFocus(self, *args):
		gobject.timeout_add(100, lambda: self.looseFocus())
		self.hasFocus = False
	

	# Events -------------------------------------------------------------------
	# --------------------------------------------------------------------------
	def submit(self, *args):
		text = self.getText()
		if len(text) <= 140 and text.strip() != "":
			self.main.send(text)
		
	def changed(self, *args):
		text = self.getText()
	
		# Cancel reply mode
		if text.strip()[0:1] != "@" and not self.isChanging:
			self.main.replyText = ""
			self.main.replyUser = ""
			self.main.replyID = -1
		
		# Remove spaces only
		if text.strip() == "":
			self.setText("")
			text = ""
		
		# Cancel all modes
		if len(text) == 0 and not self.isChanging:
			self.main.replyText = ""
			self.main.replyUser = ""
			self.main.replyID = -1
			self.main.retweetNum = -1
			self.main.retweetUser = ""
		
		# check for @ Reply
		at = self.replyRegex.match(text)
		if at != None:
			if self.main.replyID == -1:
				self.main.replyUser = at.group(1)
			else:
				if at.group(1) != self.main.replyUser:
					self.main.replyText = ""
					self.main.replyUser = at.group(1)
					self.main.replyID = -1
		
		elif self.main.replyID == -1:
			self.main.replyUser = ""
		
		# Resize
		self.resize()	
		self.isTyping = len(text) > 0
		
		# Status
		if self.isTyping:
			self.hasTyped = self.hasFocus
			if self.hasFocus:
				self.modify_text(gtk.STATE_NORMAL, self.defaultFG)
				if len(text) <= 140:
					self.gui.setStatus(lang.statusLeft % (140 - len(text)))
				
				else:
					self.gui.setStatus(lang.statusMore % (len(text) - 140))
		
		else:
			self.hasTyped = False
			self.gui.updateStatus()
		
		# Color
		self.checkColor(len(text))
	
	
	# Check the length of the text and change color if needed
	def checkColor(self, count):
		if count > 140:
			self.modify_base(gtk.STATE_NORMAL, gtk.gdk.Color(255 * 255, 200 * 255, 200 * 255))
			
		else:
			self.modify_base(gtk.STATE_NORMAL, self.defaultBG)
	
	
	# Reply / Retweet ----------------------------------------------------------
	# --------------------------------------------------------------------------
	def reply(self, num):
		self.isChanging = True
		self.grab_focus()
		text = self.getText()
		
		# Show reply text
		if num != -1:
			self.main.replyText = self.gui.html.tweets[num][0].text
	
		# Cancel Retweet
		if self.main.retweetNum > -1:
			self.main.retweetNum = -1
			self.main.retweetText = ""
			self.main.retweetUser = ""
			text = ""
		
		# Check for already existing reply
		if text[0:1] == "@":
			p = text.find(" ")
			if p == -1:
				p = len(text)
		
			text = ("@%s " % self.main.replyUser) + text[p + 1:]
	
		else:
			text = ("@%s " % self.main.replyUser) + text
	
		self.setText(text)
		self.isChanging = False
		self.checkColor(len(text))
		self.changed()
		self.modify_text(gtk.STATE_NORMAL, self.defaultFG)
		self.resize()
	
	def retweet(self):	
		self.grab_focus()
		
		# Cancel reply
		self.main.replyUser = ""
		self.main.replyID = -1

		self.isChanging = True
		text = "RT @%s: %s" % (self.main.retweetUser, self.main.retweetText)
		self.setText(text)
		
		self.isChanging = False
		self.checkColor(len(text))
		self.changed()
		self.modify_text(gtk.STATE_NORMAL, self.defaultFG)
		self.resize()
	
	
	# Sizing -------------------------------------------------------------------
	# --------------------------------------------------------------------------
	def fixSize(self):
		self.inputError = self.inputSize - self.gui.getHeight(self)
		self.resize()
		self.looseFocus()
	
	def resize(self):
		# Set Label Text
		self.gui.setLabel()
		
		# Calculate Textinput Size
		textSize = self.create_pango_context().get_font_description().get_size() / pango.SCALE
		lines = 5 if self.hasFocus else 1 
		
		# Resize
		height = self.gui.getHeight(self.gui.content)
		self.inputSize = (textSize + 4) * lines
		if self.inputError != None:
			self.inputSize += self.inputError
		
		self.gui.textScroll.set_size_request(0, self.inputSize)
		
		if lines == 1:
			self.gui.progress.set_size_request(0, self.inputSize)
		
		# Detect Error
		if self.inputError == None:
			gobject.idle_add(lambda: self.fixSize())
		
		elif not self.main.loginStatus:
			self.gui.hideAll()

	# Helpers ------------------------------------------------------------------
	# --------------------------------------------------------------------------
	def getText(self):
		return self.get_buffer().get_text(*self.get_buffer().get_bounds())

	def setText(self, text):
		self.get_buffer().set_text(text)


gtk.binding_entry_add_signal(TextInput, gtk.keysyms.Return, 0, "submit")
gtk.binding_entry_add_signal(TextInput, gtk.keysyms.KP_Enter, 0, "submit")
