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

from language import LANG as lang
from utils import REPLY_REGEX, MESSAGE_REGEX, SHORTS
from utils import Shortener

from constants import ST_CONNECT, ST_LOGIN_SUCCESSFUL, ST_WAS_RETWEET_NEW, \
                      ST_WAS_SEND, ST_WAS_RETWEET, ST_WAS_DELETE

from constants import UNSET_TEXT, UNSET_ID_NUM, MODE_MESSAGES, MODE_TWEETS


class TextInput(gtk.TextView):
    __gsignals__ = {
        'submit': (gobject.SIGNAL_RUN_LAST | gobject.SIGNAL_ACTION, None, ())
    }
    
    def __init__(self, gui):
        gtk.TextView.__init__(self)
        self.gui = gui
        self.main = gui.main
        
        # Shortener
        self.shorter = Shortener(self)
        self.shorter.setDaemon(True)
        self.shorter.start()
        if not self.main.settings['shortener'] in SHORTS:
            self.main.settings['shortener'] = SHORTS.keys()[0]
        
        # Variables
        self.initiated = False
        self.has_focus = False
        self.has_typed = False
        self.is_typing = False
        self.is_changing = False
        self.is_shortening = False
        self.change_contents = False
        self.message_len = 0
        self.message_to_send = None
        self.tweet_to_send = None
        
        # Colors
        self.default_bg = self.get_style().base[gtk.STATE_NORMAL]
        self.default_fg = self.get_style().text[gtk.STATE_NORMAL]
        
        # Setup
        self.set_border_width(0)
        self.set_wrap_mode(gtk.WRAP_WORD_CHAR)
        self.set_pixels_above_lines(2)
        self.set_pixels_below_lines(2)
        self.set_pixels_inside_wrap(0)
        self.set_left_margin(2)
        self.set_right_margin(2)
        self.set_accepts_tab(True)
        self.set_editable(True)
        self.set_cursor_visible(True)
        
        # Events
        self.connect('submit', self.submit)
        self.get_buffer().connect('changed', self.changed)
        self.connect('focus-in-event', self.focus)
        self.connect('key-press-event', self.check_keys)
    
    
    # Focus Events -------------------------------------------------------------
    # --------------------------------------------------------------------------
    def focus(self, *args):
        self.has_focus = True
        self.resize()
        if not self.has_typed:
            self.modify_text(gtk.STATE_NORMAL, self.default_fg)
            self.set_text(UNSET_TEXT)
        
        else:
            gobject.idle_add(self.check_length)
    
    def loose_focus(self):
        if not self.has_focus and self.initiated:
            self.resize()
            
            # Check if we need to toggle to message/tweet mode
            if self.message_to_send != None:
                self.switch(self.message_to_send, MODE_MESSAGES)
                self.message_to_send = None
            
            elif self.tweet_to_send != None:
                self.switch(self.tweet_to_send, MODE_TWEETS)
                self.tweet_to_send = None
            
            elif not self.has_typed:
                self.modify_text(gtk.STATE_NORMAL,
                                 self.get_style().text[gtk.STATE_INSENSITIVE])
                
                self.set_text(lang.text_entry_message \
                              if self.gui.mode == MODE_MESSAGES \
                              else lang.text_entry)
        
        return False
    
    def html_focus(self, *args):
        if self.has_focus:
            if not self.change_contents:
                gobject.timeout_add(50, self.loose_focus)
                self.has_focus = False
            
            self.change_contents = False
    
    def check_keys(self, text, event, *args):
        # Escape cancels the input
        if event.keyval == gtk.keysyms.Escape:
            self.unfocus()
            return False
        
        if event.keyval == gtk.keysyms.s:
            if event.state & gtk.gdk.CONTROL_MASK == gtk.gdk.CONTROL_MASK:
                self.reset()
                return True
    
    
    def unfocus(self):
        if self.gui.mode == MODE_TWEETS:
            self.gui.html.focus_me()
        
        elif self.gui.mode == MODE_MESSAGES:
            self.gui.message.focus_me()
    
    
    # Events -------------------------------------------------------------------
    # --------------------------------------------------------------------------
    def submit(self, *args):
        text = self.get_text().lstrip()
        if len(text) <= 140 + self.message_len and text.strip() != UNSET_TEXT:
            if self.gui.mode == MODE_MESSAGES:
                # Prevent message to be send without text
                ctext = text.strip()
                if ctext[0:1] == 'd':
                    if ctext[2:].find(' ') == -1 \
                       or self.main.message_user == UNSET_TEXT:
                       
                        self.set_text(text.lstrip())
                        return
                
                if self.main.message_user == UNSET_TEXT:
                    return
                
                ctext = ctext[2:]
                ctext = ctext[len(self.main.message_user):].strip()
                self.main.send(ctext)
            
            elif self.gui.mode == MODE_TWEETS:
                # Don't submit in edit mode when the text doesn't have been
                # edited
                if self.main.edit_text != UNSET_TEXT:
                    if self.main.edit_text.lower() == text.lower().strip():
                        return
                
                # Prevent @reply to be send without text
                ctext = text.strip()
                if ctext[0:1] in u'@\uFF20':
                    if ctext.find(' ') == -1 \
                       or self.main.reply_user == UNSET_TEXT:
                       
                        self.set_text(text.lstrip())
                        return
                
                self.main.send(ctext)
            
            else: # TODO implement search field submit
                pass
        
    def changed(self, *args):
        text = self.get_text().lstrip()
        
        # Message mode ---------------------------------------------------------
        if self.gui.mode == MODE_MESSAGES:
            # Cancel message mode
            if len(text) == 0 and not self.is_changing:
                self.unset('message')
            
            # Remove spaces only
            if text.strip() == UNSET_TEXT:
                self.set_text(UNSET_TEXT)
                text = UNSET_TEXT
            
            # check for "d user"
            msg = MESSAGE_REGEX.match(text)
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
                        
                # Remove space between username and text
                check = text[self.message_len:]
                length = len(check) - len(check.lstrip())
                if length > 0:
                    pos = self.get_buffer().get_iter_at_mark(
                                    self.get_buffer().get_insert()).get_offset()
                    
                    check = text[0:self.message_len] \
                            + text[self.message_len + length:]
                    
                    gobject.idle_add(self.clear_text, check, pos - length)
            
            elif self.main.message_id == UNSET_ID_NUM:
                self.main.message_user = UNSET_TEXT
            
            # check for "d user" and switch to messaging
            at_user = REPLY_REGEX.match(text)
            if at_user != None:
                if self.gui.load_state():
                    self.switch(self.get_text(), MODE_TWEETS)
                
                else:
                    self.tweet_to_send = self.get_text()
        
        
        # Tweet Mode -----------------------------------------------------------
        elif self.gui.mode == MODE_TWEETS:
            self.message_len = 0
            
            # Cancel reply mode
            if not text.strip()[0:1] in u'@\uFF20' \
               and not self.is_changing:
               
                self.unset('reply')
            
            # Remove spaces only
            if text.strip() == UNSET_TEXT:
                self.set_text(UNSET_TEXT)
                text = UNSET_TEXT
            
            # Cancel all modes
            if len(text) == 0 and not self.is_changing:
                self.unset('reply', 'retweet', 'edit')
            
            # check for @ Reply
            at_user = REPLY_REGEX.match(text)
            if at_user != None:
                at_len = len('@%s ' % at_user.group(1))
            
                if self.main.reply_id == UNSET_ID_NUM:
                    self.main.reply_user = at_user.group(1)
                
                else:
                    if at_user.group(1) != self.main.reply_user:
                        self.main.reply_text = UNSET_TEXT
                        self.main.reply_user = at_user.group(1)
                        self.main.reply_id = UNSET_ID_NUM
                
                # Remove space between username and text
                check = text[at_len:]
                length = len(check) - len(check.lstrip())
                if length > 0:
                    pos = self.get_buffer().get_iter_at_mark(
                                    self.get_buffer().get_insert()).get_offset()
                    
                    check = text[0:at_len] + text[at_len + length:]
                    gobject.idle_add(self.clear_text, check, pos - length)
            
            elif self.main.reply_id == UNSET_ID_NUM:
                self.main.reply_user = UNSET_TEXT
            
            # check for "d user" and switch to messaging
            msg = MESSAGE_REGEX.match(text)
            if msg != None:
                if self.gui.load_state():
                    self.switch(self.get_text(), MODE_MESSAGES)
                
                else:
                    self.message_to_send = self.get_text()
        
        
        # Strip left
        if self.get_text()[0:1] == ' ':
            ctext = self.get_text().lstrip()
            gobject.idle_add(self.clear_text, ctext)
        
        # Check for URLS to shorten
        elif not self.is_shortening:
            utext = self.get_text()
            if len(utext) >= 45 \
               and (utext.find('http') != -1 or utext.find('www') != -1):
                
                self.shorter.text = utext
        
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
    
        
    # Reply / Retweet / Message / Edit -----------------------------------------
    # --------------------------------------------------------------------------
    def reply(self):
        text = self.init_change()
        
        # Cancel Retweet
        if self.main.retweet_text != UNSET_TEXT:
            self.unset('retweet')
            text = UNSET_TEXT
        
        # Cancel Edit
        elif self.main.edit_text != UNSET_TEXT:
            self.unset('edit')
            text = UNSET_TEXT
        
        # Check for already existing reply
        if text[0:1] == '@':
            space = text.find(' ')
            if space == -1:
                space = len(text)
            
            text = ('@%s ' % self.main.reply_user) + text[space + 1:]
        
        else:
            text = ('@%s ' % self.main.reply_user) + text
        
        self.end_change(text)
    
    # Edit
    def edit(self):
        self.init_change()
        self.unset('retweet', 'reply')
        self.end_change(self.main.edit_text)
    
    # Retweet
    def retweet(self):
        self.init_change()
        self.unset('reply', 'edit')
        self.end_change('RT @%s: %s' % (self.main.retweet_user,
                                        self.main.retweet_text))
    
    # Message
    def message(self):
        text = self.init_change()
        msg = MESSAGE_REGEX.match(text)
        if msg != None:
            space = 2 + len(msg.group(1))
            text = ('d %s ' % self.main.message_user) + text[space + 1:]
        
        else:
            text = ('d %s ' % self.main.message_user) + text
        
        self.end_change(text)
    
    
    # Acceleratores ------------------------------------------------------------
    # --------------------------------------------------------------------------
    def start_tweet(self, *args):
        if not self.has_typed:
            self.is_changing = True
            self.grab_focus()
            self.set_text('')
            self.is_changing = False
    
    def start_message(self, *args):
        if not self.has_typed:
            self.is_changing = True
            self.grab_focus()
            self.set_text('d ')
            self.is_changing = False
    
    
    # Helpers ------------------------------------------------------------------
    # --------------------------------------------------------------------------
    def get_text(self):
        text = self.get_buffer().get_text(*self.get_buffer().get_bounds())
        return unicode(text)
    
    def set_text(self, text):
        self.get_buffer().set_text(text)
    
    def clear_text(self, text, pos = 0):
        self.is_shortening = False
        self.is_changing = True
        self.set_text(text)
        self.is_changing = False
        self.get_buffer().place_cursor(
                          self.get_buffer().get_iter_at_offset(pos))
    
    def shorten_text(self, text):
        if self.is_shortening:
            self.is_shortening = False
            self.set_text(text)
    
    def reset(self):
        self.set_text('')
        self.is_shortening = False
        self.has_focus = False
        self.loose_focus()
        self.unfocus()
    
    
    # Checks -------------------------------------------------------------------
    def check_length(self):
        text = self.get_text().lstrip()
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
        self.is_shortening = False
        self.has_focus = False
        self.unset('reply', 'retweet', 'edit', 'message')
        self.set_text(UNSET_TEXT)
    
    
    # Content switching --------------------------------------------------------
    def init_change(self):
        self.change_contents = True
        self.is_changing = True
        self.grab_focus()
        self.has_focus = True
        text = self.get_text()
        if not self.has_typed:
            text = ''
        
        return text
    
    def end_change(self, text):
        self.set_text(text)
        self.is_changing = False
        self.check_color(len(text))
        self.changed()
        self.modify_text(gtk.STATE_NORMAL, self.default_fg)
        self.resize()
    
    
    # Modes --------------------------------------------------------------------
    def switch(self, text, mode):
        self.change_contents = True
        self.gui.set_mode(mode)
        self.change_contents = True
        self.is_changing = True
        self.grab_focus()
        self.set_text(text.lstrip())
        self.is_changing = False
    
    def unset(self, *args):
        for key in args:
            if key == "reply":
                self.main.reply_text = UNSET_TEXT
                self.main.reply_user = UNSET_TEXT
                self.main.reply_id = UNSET_ID_NUM
            
            elif key == "retweet":
                self.main.retweet_text = UNSET_TEXT
                self.main.retweet_user = UNSET_TEXT
            
            elif key == "edit":
                self.main.edit_id = UNSET_ID_NUM
                self.main.edit_text = UNSET_TEXT
                self.main.edit_reply_id = UNSET_ID_NUM
                self.main.edit_reply_user = UNSET_TEXT
            
            elif key == "message":
                self.main.message_user = UNSET_TEXT
                self.main.message_id = UNSET_ID_NUM
                self.main.message_text = UNSET_TEXT
    
    # Other stuff --------------------------------------------------------------
    def check_refocus(self):
        if self.main.any_status(ST_WAS_SEND, ST_WAS_DELETE):
            self.gui.show_input()
            
            if not self.main.status(ST_WAS_RETWEET) \
               or (self.main.retweet_text != UNSET_TEXT \
               or self.main.reply_user != UNSET_TEXT \
               or self.main.reply_id != UNSET_ID_NUM):
                
                if self.main.status(ST_WAS_DELETE):
                    if self.has_typed:
                        self.grab_focus()
                
                elif not self.main.status(ST_WAS_RETWEET_NEW):
                    self.grab_focus()
            
            if self.has_typed \
               and self.main.any_status(ST_WAS_RETWEET_NEW, ST_WAS_DELETE):
                
                self.grab_focus()
    
    def resize(self, line_count = 5):
        self.gui.set_label()
        
        # Get Font Height
        font = self.create_pango_context().get_font_description()
        layout = self.create_pango_layout('')
        layout.set_markup('WTF?!')
        layout.set_font_description(font)
        text_size = layout.get_pixel_size()[1]
        
        # Resize
        lines = line_count if self.has_focus else 1
        input_size = int((text_size + (6 if lines == 1 else 1.5)) * lines)
        self.gui.text_scroll.set_size_request(0, input_size)
        
        if lines == 1:
            self.gui.progress.set_size_request(0, input_size)
        
        if not self.initiated:
            self.initiated = True
            self.loose_focus()
        
        if not self.main.any_status(ST_LOGIN_SUCCESSFUL, ST_CONNECT):
            self.gui.hide_all()


gtk.binding_entry_add_signal(TextInput, gtk.keysyms.Return, 0, 'submit')
gtk.binding_entry_add_signal(TextInput, gtk.keysyms.KP_Enter, 0, 'submit')

