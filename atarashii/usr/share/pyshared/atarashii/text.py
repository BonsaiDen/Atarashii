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
import gobject
import pango

import re

from lang import lang
from constants import UNSET_TEXT, UNSET_ID_NUM, MODE_MESSAGES, MODE_TWEETS


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
        self.has_focus = False
        self.is_typing = False
        self.has_typed = False
        self.is_changing = False
        self.change_contents = False
        self.reply_regex = re.compile(ur"\B[@\uFF20]([a-z0-9_]{1,20})\s.*",
                                     re.UNICODE | re.IGNORECASE)
        
        self.message_regex = re.compile('d ([a-z0-9_]{1,20})\s.*',
                                       re.UNICODE | re.IGNORECASE)
        
        self.message_len = 0
        self.go_send_message = None
        
        # Sizes
        self.input_size = None
        self.input_error = None
        
        # Colors
        self.default_bg = self.get_style().base[gtk.STATE_NORMAL]
        self.default_fg = self.get_style().text[gtk.STATE_NORMAL]
        
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
        self.has_focus = True
        self.resize()
        if not self.has_typed:
            self.modify_text(gtk.STATE_NORMAL, self.default_fg)
            self.set_text(UNSET_TEXT)
        
        else:
            gobject.idle_add(lambda: self.check_length())
    
    def loose_focus(self):
        if not self.has_focus and self.input_error != None:
            self.resize()
            
            # Check if we need to toggle to message mode
            if self.go_send_message != None:
                self.switch_to_message(self.go_send_message)
                self.go_send_message = None
            
            elif not self.has_typed:
                self.modify_text(gtk.STATE_NORMAL,
                                self.get_style().text[gtk.STATE_INSENSITIVE])
                
                self.set_text(
                    lang.text_entry_message if self.gui.mode == MODE_MESSAGES \
                    else lang.text_entry)
        
        return False
    
    def html_focus(self, *args):
        if self.has_focus:
            if not self.change_contents:
                gobject.timeout_add(50, lambda: self.loose_focus())
                self.has_focus = False
            
            self.change_contents = False
    
    
    # Events -------------------------------------------------------------------
    # --------------------------------------------------------------------------
    def submit(self, *args):
        text = self.get_text()
        if len(text) <= 140 + self.message_len and text.strip() != UNSET_TEXT:
            if self.gui.mode == MODE_MESSAGES:
                if self.main.message_user != UNSET_TEXT:
                    text = text[2:]
                    text = text[len(self.main.message_user):].strip()
                    self.main.send(text)
            
            elif self.gui.mode == MODE_TWEETS:
                self.main.send(text)
            
            else: # TODO implement search field submit
                pass
    
    def changed(self, *args):
        text = self.get_text()
        
        # Message mode ---------------------------------------------------------
        if self.gui.mode == MODE_MESSAGES:
            # Cancel reply mode
            if len(text) == 0 and not self.is_changing:
                self.main.message_user = UNSET_TEXT
                self.main.message_id = UNSET_ID_NUM
                self.main.message_text = UNSET_TEXT
            
            # check for "d user"
            msg = self.message_regex.match(text)
            self.message_len = 0
            if msg != None:
                self.message_len = len('d %s ' % msg.group(1))
                
                if self.main.message_id == UNSET_ID_NUM:
                    self.main.message_user = msg.group(1)
                else:
                    if msg.group(1) != self.main.message_user:
                        self.main.message_text = UNSET_TEXT
                        self.main.message_user = msg.group(1)
                        self.main.message_id = UNSET_ID_NUM
            
            elif self.main.message_id == UNSET_ID_NUM:
                self.main.message_user = UNSET_TEXT
        
        
        # Tweet Mode -----------------------------------------------------------
        elif self.gui.mode == MODE_TWEETS:
            self.message_len = 0
            
            # Cancel reply mode
            if not unicode(text.strip())[0:1] in u"@\uFF20" and \
               not self.is_changing:
                self.main.reply_text = UNSET_TEXT
                self.main.reply_user = UNSET_TEXT
                self.main.reply_id = UNSET_ID_NUM
                
            # Remove spaces only
            if text.strip() == UNSET_TEXT:
                self.set_text(UNSET_TEXT)
                text = UNSET_TEXT
            
            # Cancel all modes
            if len(text) == 0 and not self.is_changing:
                self.main.reply_text = UNSET_TEXT
                self.main.reply_user = UNSET_TEXT
                self.main.reply_id = UNSET_ID_NUM
                self.main.reweetText = UNSET_TEXT
                self.main.retweet_user = UNSET_TEXT
            
            # check for @ Reply
            at_user = self.reply_regex.match(text)
            if at_user != None:
                if self.main.reply_id == UNSET_ID_NUM:
                    self.main.reply_user = at_user.group(1)
                
                else:
                    if at_user.group(1) != self.main.reply_user:
                        self.main.reply_text = UNSET_TEXT
                        self.main.reply_user = at_user.group(1)
                        self.main.reply_id = UNSET_ID_NUM
            
            elif self.main.reply_id == UNSET_ID_NUM:
                self.main.reply_user = UNSET_TEXT
            
            # check for "d user" and switch to messaging
            msg = self.message_regex.match(text)
            if msg != None:
                if self.gui.is_ready():
                    self.switch_to_message(self.get_text())
                
                else:
                    self.go_send_message = self.get_text()
        
        # Resize
        self.resize()
        self.is_typing = len(text) > 0
        
        # Status
        if self.is_typing:
            self.has_typed = self.has_focus
            if self.has_focus:
                self.modify_text(gtk.STATE_NORMAL, self.default_fg)
                self.check_length()
        
        else:
            if not self.is_changing:
                self.change_contents = False
            
            self.has_typed = False
            self.gui.update_status()
        
        self.check_color(len(text))
    
    def check_length(self):
        text = self.get_text()
        max_length = 140 + self.message_len
        if len(text) <= max_length:
            self.gui.set_status(lang.status_left % (max_length - len(text)))
        
        else:
            self.gui.set_status(lang.status_more % (len(text) - max_length))
    
    def check_color(self, count):
        if count > 140 + self.message_len:
            self.modify_base(gtk.STATE_NORMAL,
                             gtk.gdk.Color(255 * 255, 200 * 255, 200 * 255))
        
        else:
            self.modify_base(gtk.STATE_NORMAL, self.default_bg)
    
    def check_mode(self):
        self.has_focus = False
        self.main.reply_text = UNSET_TEXT
        self.main.reply_user = UNSET_TEXT
        self.main.reply_id = UNSET_ID_NUM
        self.main.retweet_text = UNSET_TEXT
        self.main.retweet_user = UNSET_TEXT
        self.main.message_user = UNSET_TEXT
        self.main.message_id = UNSET_ID_NUM
        self.main.message_text = UNSET_TEXT
        self.set_text(UNSET_TEXT)
    
    
    # Reply / Retweet / Message ------------------------------------------------
    # --------------------------------------------------------------------------
    def reply(self):
        self.change_contents = True
        self.is_changing = True
        self.grab_focus()
        text = self.get_text()
        
        # Cancel Retweet
        if self.main.retweet_text != UNSET_TEXT:
            self.main.retweet_text = UNSET_TEXT
            self.main.retweet_user = UNSET_TEXT
            text = UNSET_TEXT
        
        # Check for already existing reply
        if text[0:1] == "@":
            space = text.find(" ")
            if space == -1:
                space = len(text)
            
            text = ("@%s " % self.main.reply_user) + text[space + 1:]
        
        else:
            text = ("@%s " % self.main.reply_user) + text
        
        self.set_text(text)
        self.is_changing = False
        self.check_color(len(text))
        self.changed()
        self.modify_text(gtk.STATE_NORMAL, self.default_fg)
        self.resize()
    
    def retweet(self):    
        self.change_contents = True
        self.is_changing = True
        self.grab_focus()
        self.has_focus = True
        
        # Cancel reply
        self.main.reply_user = UNSET_TEXT
        self.main.reply_id = UNSET_ID_NUM
        text = "RT @%s: %s" % (self.main.retweet_user, self.main.retweet_text)
        self.set_text(text)
        
        self.is_changing = False
        self.check_color(len(text))
        self.changed()
        self.modify_text(gtk.STATE_NORMAL, self.default_fg)
        self.resize()
    
    def message(self):
        self.change_contents = True
        self.is_changing = True
        self.grab_focus()
        text = self.get_text()
        
        # Check for already existing message
        msg = self.message_regex.match(text)
        if msg != None:
            space = 2 + len(msg.group(1))
            text = ("d %s " % self.main.message_user) + text[space + 1:]
        
        else:
            text = ("d %s " % self.main.message_user) + text
        
        self.set_text(text)
        self.is_changing = False
        self.check_color(len(text))
        self.changed()
        self.modify_text(gtk.STATE_NORMAL, self.default_fg)
        self.resize()
    
    def switch_to_message(self, text):
        self.change_contents = True
        self.gui.set_mode(MODE_MESSAGES)
        self.change_contents = True
        self.is_changing = True
        self.grab_focus()
        self.set_text(text)
        self.is_changing = False
    
    
    # Sizing -------------------------------------------------------------------
    # --------------------------------------------------------------------------
    def fix_size(self):
        self.input_error = self.input_size - self.gui.get_height(self)
        self.resize()
        self.loose_focus()
    
    def resize(self, line_count = 5):
        # Set Label Text
        self.gui.set_label()
        
        # Calculate Textinput Size
        psize = self.create_pango_context().get_font_description().get_size()
        text_size = psize / pango.SCALE
        lines = line_count if self.has_focus else 1
        
        # Resize
        self.input_size = (text_size + 4) * lines
        if self.input_error != None:
            self.input_size += self.input_error
        
        self.gui.text_scroll.set_size_request(0, self.input_size)
        
        if lines == 1:
            self.gui.progress.set_size_request(0, self.input_size)
        
        # Detect Error
        if self.input_error == None:
            gobject.idle_add(lambda: self.fix_size())
        
        elif not self.main.login_status and not self.main.is_connecting:
            self.gui.hide_all()
    
    
    # Helpers ------------------------------------------------------------------
    # --------------------------------------------------------------------------
    def get_text(self):
        return self.get_buffer().get_text(*self.get_buffer().get_bounds())
    
    def set_text(self, text):
        self.get_buffer().set_text(text)


gtk.binding_entry_add_signal(TextInput, gtk.keysyms.Return, 0, "submit")
gtk.binding_entry_add_signal(TextInput, gtk.keysyms.KP_Enter, 0, "submit")

