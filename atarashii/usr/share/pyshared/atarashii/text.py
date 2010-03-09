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
		self.changeContents = False
		self.replyRegex = re.compile('@([^\s]+)\s.*')
		self.messageRegex = re.compile('d ([^\s]+)\s.*')
		
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
			
		else:
			gobject.idle_add(lambda: self.checkLength())
	
	def looseFocus(self):
		if not self.hasFocus and self.inputError != None:
			self.resize()
			if not self.hasTyped:
				self.modify_text(gtk.STATE_NORMAL, 
								self.get_style().text[gtk.STATE_INSENSITIVE])
				self.get_buffer().set_text(
					lang.textEntryMessage if self.gui.mode else lang.textEntry)

		return False
	
	def htmlFocus(self, *args):
		if self.hasFocus:
			if not self.changeContents:
				gobject.timeout_add(50, lambda: self.looseFocus())
				self.hasFocus = False
			
			self.changeContents = False
		
	
	# Events -------------------------------------------------------------------
	# --------------------------------------------------------------------------
	def submit(self, *args):
		text = self.getText()
		if len(text) <= 140 and text.strip() != "":
			if self.gui.mode:
				if self.main.messageUser != "":
					text = text[2:]
					text = text[len(self.main.messageUser):].strip()
					self.main.send(text)
				
			else:
				self.main.send(text)
		
	def changed(self, *args):
		text = self.getText()
	
		# Message mode ---------------------------------------------------------
		if self.gui.mode:
			# Cancel reply mode
			if len(text) == 0 and not self.isChanging:
				self.main.messageUser = ""
				self.main.messageID = -1
				self.main.messageText = ""
	
			# check for @ Reply
			msg = self.messageRegex.match(text)
			if msg != None:
				if self.main.messageID == -1:
					self.main.messageUser = msg.group(1)
				else:
					if msg.group(1) != self.main.messageUser:
						self.main.messageText = ""
						self.main.messageUser = msg.group(1)
						self.main.messageID = -1
		
			elif self.main.messageID == -1:
				self.main.messageUser = ""
	
	
		# Tweet Mode -----------------------------------------------------------
		else:
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
				self.checkLength()
		
		else:
			if not self.isChanging:
				self.changeContents = False
			
			self.hasTyped = False
			self.gui.updateStatus()
		
		# Color
		self.checkColor(len(text))
	
	
	def checkLength(self):
		text = self.getText()
		if len(text) <= 140:
			self.gui.setStatus(lang.statusLeft % (140 - len(text)))
		
		else:
			self.gui.setStatus(lang.statusMore % (len(text) - 140))

	# Check the length of the text and change color if needed
	def checkColor(self, count):
		if count > 140:
			self.modify_base(gtk.STATE_NORMAL, 
								gtk.gdk.Color(255 * 255, 200 * 255, 200 * 255))
			
		else:
			self.modify_base(gtk.STATE_NORMAL, self.defaultBG)
	
	def checkMode(self):
		self.hasFocus = False
		self.main.replyText = ""
		self.main.replyUser = ""
		self.main.replyID = -1
		self.main.retweetNum = -1
		self.main.retweetUser = ""
		self.main.messageUser = ""
		self.main.messageID = -1
		self.main.messageText = ""
		self.setText("")
	
	# Reply / Retweet / Message ------------------------------------------------
	# --------------------------------------------------------------------------
	def reply(self):
		self.changeContents = True
		self.isChanging = True
		self.grab_focus()
		text = self.getText()
		
		# Cancel Retweet
		if self.main.retweetNum > -1 or self.main.retweetText != "":
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
		self.changeContents = True
		self.isChanging = True
		self.grab_focus()
		self.hasFocus = True
		
		# Cancel reply
		self.main.replyUser = ""
		self.main.replyID = -1
		text = "RT @%s: %s" % (self.main.retweetUser, self.main.retweetText)
		self.setText(text)
		
		self.isChanging = False
		self.checkColor(len(text))
		self.changed()
		self.modify_text(gtk.STATE_NORMAL, self.defaultFG)
		self.resize()
	
	def message(self):
		self.changeContents = True
		self.isChanging = True
		self.grab_focus()
		text = self.getText()

		# Check for already existing message
		msg = self.messageRegex.match(text)
		if msg != None:
			p = 2 + len(msg.group(1))
			text = ("d %s " % self.main.messageUser) + text[p + 1:]
		
		else:
			text = ("d %s " % self.main.messageUser) + text
	
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
		
	
	def resize(self, lineCount = 5):
		# Set Label Text
		self.gui.setLabel()
		
		# Calculate Textinput Size
		psize = self.create_pango_context().get_font_description().get_size() 
		textSize = psize / pango.SCALE
		lines = lineCount if self.hasFocus else 1 
		
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
		
		elif not self.main.loginStatus and not self.main.isConnecting:
			self.gui.hideAll()

	# Helpers ------------------------------------------------------------------
	# --------------------------------------------------------------------------
	def getText(self):
		return self.get_buffer().get_text(*self.get_buffer().get_bounds())

	def setText(self, text):
		self.get_buffer().set_text(text)


gtk.binding_entry_add_signal(TextInput, gtk.keysyms.Return, 0, "submit")
gtk.binding_entry_add_signal(TextInput, gtk.keysyms.KP_Enter, 0, "submit")
