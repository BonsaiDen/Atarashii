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

from constants import REPLY_REGEX, MESSAGE_REGEX
from utils import URLShorter
from language import LANG as lang

from constants import MSG_SIGN, AT_SIGNS
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
        self.buffer = self.get_buffer()
        
        # Variables
        self.initiated = False
        self.has_focus = False
        self.has_typed = False
        self.is_typing = False
        self.is_changing = False
        self.is_shortening = False
        self.is_pasting = False
        self.change_contents = False
        self.message_len = 0
        self.message_to_send = None
        self.tweet_to_send = None
        
        # Auto complete stuff
        self.auto_complete_name = UNSET_TEXT
        self.user_offset = 0
        self.user_complete = False
        self.auto_complete = False
        self.auto_typed = UNSET_TEXT
        self.backspace = False
        
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
        self.connect('focus-in-event', self.focus)
        self.connect('key-press-event', self.check_keys)
        
        self.connect('submit', self.on_submit)
        self.connect('paste-clipboard', self.on_paste)
        self.connect('move-cursor', self.on_move)
        self.connect('button-press-event', self.on_move)
        
        self.buffer.connect('changed', self.on_changed)
        self.buffer.connect('insert-text', self.on_insert)
    
    
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
            if self.message_to_send is not None:
                self.switch(self.message_to_send, MODE_MESSAGES)
                self.message_to_send = None
            
            elif self.tweet_to_send is not None:
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
        control = event.state & gtk.gdk.CONTROL_MASK == gtk.gdk.CONTROL_MASK
        self.backspace = False
        
        # Cancel auto complete via move
        i = gtk.keysyms
        if event.keyval in (i.Up, i.Down, i.Right, i.Left, i.Page_Up,
                            i.Page_Down, i.End, i.Begin, 65360, i.KP_Up,
                            i.KP_Down, i.KP_Left, i.KP_Right, i.KP_Page_Up,
                            i.KP_Page_Down, i.KP_End, i.KP_Begin) \
                        and self.auto_complete:
            
            self.remove_auto_complete()
            return False
        
        if event.keyval == gtk.keysyms.space:
            pos = self.get_cursor_pos()
            if pos == 0:
                return True
            
            self.remove_auto_complete()
            return False
        
        # Escape cancels the input
        if event.keyval == gtk.keysyms.Escape:
            self.remove_auto_complete()
            self.unfocus()
            return False
        
        # Cancel auto complete with backsapce
        auto = self.auto_complete
        if event.keyval == gtk.keysyms.BackSpace:
            self.backspace = True
            if auto:
                self.remove_auto_complete()
                return True
            
            else:
                self.auto_complete = False
                return False
        
        self.auto_complete = False
        
        # Finish auto complete with return or tab
        if event.keyval in (gtk.keysyms.Return, gtk.keysyms.Tab) and auto:
            text = self.get_text()
            if not ' ' in text:
                text += ' '
                self.is_changing = True
                self.set_text(text)
                self.is_changing = False
            
            self.auto_typed = UNSET_TEXT
            if not self.user_complete:
                self.set_cursor(self.get_offset(len(text) + 1))
            
            else:
                self.set_cursor(self.get_offset(self.user_offset))
            
            return True
        
        # Tab skips to the end
        if event.keyval == gtk.keysyms.Tab:
            self.set_cursor(self.get_offset(len(self.get_text())))
            return True
        
        # CRTL + S stops any input
        if event.keyval == gtk.keysyms.s and control:
            self.reset()
            return True
        
        # Shift + Return will start a new tweet/message right after submission
        if (self.main.reply_user != UNSET_TEXT \
           or self.main.message_user != UNSET_TEXT \
           or self.gui.mode == MODE_TWEETS) \
           and event.keyval == gtk.keysyms.Return \
           and event.state & gtk.gdk.SHIFT_MASK == gtk.gdk.SHIFT_MASK:
            
            self.on_submit(self, True)
            return True
        
        # Take care of misplaced newlines
        if event.keyval == gtk.keysyms.Return and control:
            pos = self.get_cursor_pos()
            if pos == 0:
                return True
            
            text = self.get_text().strip()
            if len(text) > 0 and not text[0] in AT_SIGNS + MSG_SIGN:
                return False
            
            spaces = text.count(' ')
            if self.gui.mode == MODE_TWEETS:
                if spaces > 0:
                    return False
            
            elif self.gui.mode == MODE_MESSAGES:
                if spaces > 1:
                    return False
            
            return True
    
    def unfocus(self):
        if self.gui.mode == MODE_TWEETS:
            self.gui.html.focus_me()
        
        elif self.gui.mode == MODE_MESSAGES:
            self.gui.message.focus_me()
    
    
    # Events -------------------------------------------------------------------
    # --------------------------------------------------------------------------
    def on_submit(self, textbox, multi=False):
        text = self.get_text().lstrip()
        if len(text) <= 140 + self.message_len and text.strip() != UNSET_TEXT \
           and self.gui.is_text_mode():
            
            if self.gui.mode == MODE_MESSAGES:
                
                # Prevent message to be send without text
                ctext = text.strip()
                if ctext[0:1] == MSG_SIGN:
                    if ctext[2:].find(' ') == -1 \
                       or self.main.message_user == UNSET_TEXT:
                        
                        self.is_changing = True
                        self.set_text(text.lstrip())
                        self.is_changing = False
                        return False
                
                if self.main.message_user == UNSET_TEXT:
                    return False
                
                ctext = ctext[2:]
                ctext = ctext[len(self.main.message_user):].strip()
                self.main.send(ctext, multi)
            
            elif self.gui.mode == MODE_TWEETS:
                
                # Don't submit in edit mode when the text doesn't have been
                # edited
                if self.main.edit_text != UNSET_TEXT:
                    if self.main.edit_text.lower() == text.lower().strip():
                        return False
                
                # Prevent submitting something that looks like a message and \
                # therefore won't return a tweet since twitter thinks that you
                # wanted to send a DM
                ctext = text.strip()
                if text.lstrip()[0:2] == MSG_SIGN + ' ' or ctext == MSG_SIGN:
                    return False
                
                # Prevent @reply to be send without text
                if ctext[0:1] in AT_SIGNS:
                    if ctext.find(' ') == -1 \
                       or self.main.reply_user == UNSET_TEXT:
                        
                        self.is_changing = True
                        self.set_text(text.lstrip())
                        self.is_changing = False
                        return False
                
                self.main.send(ctext, multi)
            
            # TODO implement search field submit
            else:
                pass
    
    def on_paste(self, view):
        self.is_pasting = True
    
    def on_insert(self, buf, itr, text, length):
        if self.is_pasting:
            if text.find('http') != -1 or text.find('www') != -1:
                URLShorter(text, self)
            
            self.is_pasting = False
    
    def on_changed(self, *args):
        text = self.get_text().lstrip()
        
        # Message mode ---------------------------------------------------------
        if self.gui.mode == MODE_MESSAGES:
            
            # Cancel message mode
            if len(text) == 0 and not self.is_changing:
                self.main.unset('message')
            
            # Remove spaces only
            if text.strip() == UNSET_TEXT:
                self.set_text(UNSET_TEXT)
                text = UNSET_TEXT
            
            # check for 'd user'
            msg = MESSAGE_REGEX.match(text)
            self.message_len = 0
            
            # Remove whitespace between 'd' and username
            if len(text) > 2 and text[2].strip(' \n\t\r\v') == UNSET_TEXT:
                gobject.idle_add(self.clear_text,
                                 MSG_SIGN + ' ' + text[1:].lstrip(), 2)
            
            elif msg is not None:
                self.message_len = len('%s %s ' % (MSG_SIGN, msg.group(1)))
                
                if self.main.message_user_id == UNSET_ID_NUM:
                    self.main.message_user = msg.group(1)
                
                elif msg.group(1) != self.main.message_user:
                    self.main.message_text = UNSET_TEXT
                    self.main.message_user = msg.group(1)
                    self.main.message_user_id = UNSET_ID_NUM
                
                # Remove space between username and text
                check = text[self.message_len:]
                length = len(check) - len(check.lstrip())
                if length > 0:
                    gobject.idle_add(self.clear_text,
                                     text[0:self.message_len] \
                                     + text[self.message_len + length:],
                                     (self.message_len + length) - 1)
            
            elif self.main.message_user_id == UNSET_ID_NUM:
                self.main.message_user = UNSET_TEXT
            
            
            
            # check for '@user' and switch to tweeting
            at_user = REPLY_REGEX.match(text)
            if at_user is not None:
                if self.gui.load_state():
                    self.switch(self.get_text(), MODE_TWEETS)
                
                else:
                    self.tweet_to_send = self.get_text()
        
        
        # Tweet Mode -----------------------------------------------------------
        elif self.gui.mode == MODE_TWEETS:
            self.message_len = 0
            
            # Cancel reply mode
            if not text.strip()[0:1] in AT_SIGNS and not self.is_changing:
                self.main.unset('reply')
            
            # Remove spaces only
            if text.strip() == UNSET_TEXT:
                self.set_text(UNSET_TEXT)
                text = UNSET_TEXT
            
            # Cancel all modes
            if len(text) == 0 and not self.is_changing:
                self.main.unset('reply', 'retweet', 'edit')
            
            # check for @ Reply
            at_user = REPLY_REGEX.match(text)
            if at_user is not None:
                at_len = len('%s%s ' % (lang.tweet_at, at_user.group(1)))
                
                if self.main.reply_id == UNSET_ID_NUM:
                    self.main.reply_user = at_user.group(1)
                
                elif at_user.group(1) != self.main.reply_user:
                    self.main.reply_text = UNSET_TEXT
                    self.main.reply_user = at_user.group(1)
                    self.main.reply_id = UNSET_ID_NUM
                
                # Remove space between username and text
                check = text[at_len:]
                length = len(check) - len(check.lstrip())
                if length > 0:
                    gobject.idle_add(self.clear_text,
                                     text[0:at_len] + text[at_len + length:],
                                     (at_len + length) - 1)
            
            elif self.main.reply_id == UNSET_ID_NUM:
                self.main.reply_user = UNSET_TEXT
            
            # check for 'd user' and switch to messaging
            msg = MESSAGE_REGEX.match(text)
            if msg is not None:
                if self.gui.load_state():
                    self.switch(self.get_text(), MODE_MESSAGES)
                
                else:
                    self.message_to_send = self.get_text()
        
        # Strip left
        space = self.get_text()[0:1]
        if space.strip() != space:
            ctext = self.get_text().lstrip()
            gobject.idle_add(self.clear_text, ctext)
        
        # Auto completion
        self.check_auto_complete()
        
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
    
    
    # Auto completion of usernames ---------------------------------------------
    # --------------------------------------------------------------------------
    def on_move(self, *args):
        self.remove_auto_complete()
    
    def check_auto_complete(self):
        if self.is_changing or self.backspace:
            return False
        
        # Extract @user and 'd user'
        end_mark = self.get_insert(True)
        pre_text = self.get_text(self.get_offset(0), end_mark).lstrip()
        auto = False
        offset = 0
        if len(pre_text) > 2:
            if pre_text[0:2] == MSG_SIGN + ' ':
                user_text = pre_text[2:]
                if len(user_text) > 1 and not ' ' in user_text:
                    auto = True
                    offset = 2
            
            elif pre_text[0] in AT_SIGNS and not ' ' in pre_text:
                user_text = pre_text[1:]
                auto = True
                offset = 1
        
        # @user completion
        self.user_complete = False
        if not auto:
            pos = pre_text.rfind('@')
            if pos == -1:
                pos = pre_text.rfind(u'\uFF20')
            
            if pos != -1:
                offset = pos + 1
                user_text = pre_text[offset:]
                if len(user_text) > 1:
                    auto = True
                    self.user_complete = True
        
        # Insert completion stuff
        if auto:
            name = None
            for i in self.main.settings.user_list:
                if i.lower().startswith(user_text.lower()):
                    name = i
                    break
            
            # Store original typing
            diff = len(user_text) - len(self.auto_typed)
            if diff >= 0 or len(self.auto_typed) == 0:
                self.auto_typed += user_text[len(user_text) - diff:]
            
            else:
                self.auto_typed = self.auto_typed[:-(diff)]
            
            # Suggest a username
            if name is not None and len(name) > len(user_text):
                
                # Calculate remaining completion text stuff
                all_text = self.get_text()
                end_pos = end_mark.get_offset()
                off = offset + len(self.auto_complete_name) + 1 \
                      if self.auto_complete else end_pos
                
                self.auto_complete_name = name
                
                # Set text
                self.is_changing = True
                pre = all_text[0:offset] + name
                self.set_text(pre + ' ' + all_text[off:].lstrip())
                self.user_offset = len(pre) + 1
                self.is_changing = False
                
                # Move cursor and selection
                self.auto_complete = True
                start = self.get_offset(end_pos)
                auto_end = end_pos + len(name) - end_pos + offset
                self.buffer.move_mark(self.get_insert(), start)
                self.buffer.select_range(start, self.get_offset(auto_end))
            
            else:
                self.remove_auto_complete()
    
    def remove_auto_complete(self):
        if self.auto_complete:
            self.is_changing = True
            
            # Retrieve text before deleting the selection!
            text = self.get_text()
            
            # Replace text with the one that was originally typed
            select = self.buffer.get_selection_bounds()
            if len(select) > 0:
                self.buffer.delete(select[0], select[1])
            
            pos = (self.user_offset - len(self.auto_complete_name)) - 1
            pre = text[:pos] + self.auto_typed
            dec = 1 if self.backspace else 0
            self.set_text(pre + text[self.user_offset - dec:])
            
            # Move cursor
            self.set_cursor(self.get_offset(len(pre)))
            self.is_changing = False
            self.auto_complete = False
        
        self.auto_typed = UNSET_TEXT
        self.auto_complete_name = UNSET_TEXT
    
    
    # Reply / Retweet / Message / Edit -----------------------------------------
    # --------------------------------------------------------------------------
    def reply(self, multi=False):
        text = self.init_change()
        
        # Cancel Retweet
        if self.main.retweet_text != UNSET_TEXT:
            self.main.unset('retweet')
            text = UNSET_TEXT
        
        # Cancel Edit
        elif self.main.edit_text != UNSET_TEXT:
            self.main.unset('edit')
            text = UNSET_TEXT
        
        # Check for already existing reply
        if text[0:1] in AT_SIGNS:
            space = text.find(' ')
            if space == -1:
                space = len(text)
            
            text = ('%s%s ' % (lang.tweet_at,  self.main.reply_user)) \
                   + (text[space + 1:] if not multi else UNSET_TEXT)
        
        else:
            text = ('%s%s ' % (lang.tweet_at, self.main.reply_user)) + text
        
        self.end_change(text)
    
    # Edit
    def edit(self):
        self.init_change()
        self.main.unset('retweet', 'reply')
        self.end_change(self.main.edit_text)
    
    # Retweet
    def retweet(self):
        self.init_change()
        self.main.unset('reply', 'edit')
        self.end_change('RT %s%s: %s' % (lang.tweet_at, self.main.retweet_user,
                                         self.main.retweet_text))
    
    # Message
    def message(self, multi=False):
        text = self.init_change()
        msg = MESSAGE_REGEX.match(text)
        if msg is not None:
            space = 2 + len(msg.group(1))
            text = ('%s %s ' % (MSG_SIGN, self.main.message_user)) \
                   + (text[space + 1:] if not multi else UNSET_TEXT)
        
        else:
            text = ('%s %s ' % (MSG_SIGN, self.main.message_user)) + text
        
        self.end_change(text)
    
    
    # Acceleratores ------------------------------------------------------------
    # --------------------------------------------------------------------------
    def start_tweet(self, *args):
        if not self.has_typed or self.get_text().strip() == MSG_SIGN:
            self.gui.set_mode(MODE_TWEETS)
            self.is_changing = True
            self.grab_focus()
            self.set_text(UNSET_TEXT)
            self.is_changing = False
        
        elif self.gui.mode == MODE_TWEETS:
            self.grab_focus()
    
    def start_message(self, *args):
        if not self.has_typed:
            self.gui.set_mode(MODE_MESSAGES)
            self.is_changing = True
            self.grab_focus()
            self.set_text(MSG_SIGN + ' ')
            self.is_changing = False
        
        elif self.gui.mode == MODE_MESSAGES:
            self.grab_focus()
    
    
    # Helpers ------------------------------------------------------------------
    # --------------------------------------------------------------------------
    def get_text(self, start=None, end=None):
        if start is not None:
            return unicode(self.buffer.get_text(start, end))
        
        else:
            return unicode(self.buffer.get_text(*self.buffer.get_bounds()))
    
    def set_text(self, text):
        self.buffer.set_text(text)
    
    def get_offset(self, offset):
        return self.buffer.get_iter_at_offset(offset)
    
    def get_insert(self, mark=False):
        insert = self.buffer.get_insert()
        if mark:
            return self.buffer.get_iter_at_mark(insert)
        
        else:
            return insert
    
    def get_cursor_pos(self):
        return self.buffer.get_iter_at_mark(self.get_insert()).get_offset()
    
    def set_cursor(self, pos):
        self.buffer.move_mark(self.get_insert(), pos)
        self.buffer.select_range(pos, pos)
    
    def clear_text(self, text, pos=0):
        self.auto_complete = False
        self.is_shortening = False
        self.is_changing = True
        self.set_text(text)
        self.is_changing = False
        if len(text.strip()) == pos:
            pos = len(text)
        
        self.buffer.place_cursor(
                          self.get_offset(pos))
    
    def shorten_text(self, text):
        if self.is_shortening:
            self.is_shortening = False
            self.set_text(text)
    
    def reset(self):
        self.set_text(UNSET_TEXT)
        self.auto_complete = False
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
        self.main.unset('reply', 'retweet', 'edit', 'message')
        self.set_text(UNSET_TEXT)
    
    
    # Content switching --------------------------------------------------------
    def init_change(self):
        self.change_contents = True
        self.is_changing = True
        self.grab_focus()
        self.has_focus = True
        text = self.get_text()
        if not self.has_typed:
            text = UNSET_TEXT
        
        return text
    
    def end_change(self, text):
        self.set_text(text)
        self.is_changing = False
        self.check_color(len(text))
        self.on_changed()
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
    
    def resize(self, line_count=5):
        self.gui.set_label()
        
        # Get Font Height
        font = self.create_pango_context().get_font_description()
        layout = self.create_pango_layout(UNSET_TEXT)
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

