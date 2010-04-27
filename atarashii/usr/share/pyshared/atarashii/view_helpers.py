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


# HTML View / Helpers ----------------------------------------------------------
# ------------------------------------------------------------------------------
import pygtk
pygtk.require('2.0')
import gtk
import gobject

import time
import math

from utils import gmtime, localtime
from language import LANG as lang


# Did you ever see faked mouse move events which fixed CSS bugs? ---------------
# No? Then see down below ------------------------------------------------------
class ViewHelpers(object):
    def copy_to_clipboard(self, data):
        display = gtk.gdk.display_manager_get().get_default_display()
        clipboard = gtk.Clipboard(display, 'CLIPBOARD')
        clipboard.set_text(data)
        
        # Make sure the textbox doesn't loose focus if it's opened
        if self.text.has_focus:
            gobject.idle_add(self.text.grab_focus)
    
    def copy_link(self, menu, uri):
        self.copy_to_clipboard(uri)
    
    def copy_tweet(self, menu, uri, item):
        user = self.get_user(item)
        text = self.get_text(item)
        self.copy_to_clipboard('%s%s\n%s' \
                               % (lang.tweet_at, user.screen_name, text))
    
    def copy_message(self, menu, uri, item):
        user = self.get_user(item)
        text = self.get_text(item)
        self.copy_to_clipboard('%s%s\n%s' \
                               % (lang.tweet_at, user.screen_name, text))
    
    def copy_tag(self, menu, tag):
        self.copy_to_clipboard(tag)
    
    
    # Scrolling ----------------------------------------------------------------
    # --------------------------------------------------------------------------
    def get_offset(self):
        try:
            self.execute_script(
                '''document.title=
                   document.getElementById('newcontainer').offsetHeight;''')
            
            return int(self.get_main_frame().get_title())
        
        except Exception:
            return 0
    
    def loaded(self, view, state, force=False):
        # HACK! The value of the constant might change, but currently it's not
        # exposed to pygtk webkit and since the 'load-finished' signal is
        # deprecated, it's a 50/50 chance that one of those will eventually
        # break the whole thing.. so do you want to be eaten by the tiger
        # or the lion?
        # Note from Ivo: Actually, the Lion won't eat me since I'm one too ;D
        if self.get_property('load-status') != 2 and not force:
            return False
        
        else:
            self.is_loading = False
        
        if not self.gui.is_shown:
            return False
        
        # Offset
        if len(self.items) > 0 and self.has_newitems \
           and not self.load_history:
            offset = self.get_offset()
        
        else:
            offset = 0
        
        # Fix for wrong offset when lots of tweets are loading and the user
        # has scrolled since the rendering was started
        self.position += self.current_scroll - self.position
        
        # Re-scroll
        if not self.first_load and self.position > 0:
            pos = self.position + offset
            self.check_scroll(pos)
            gobject.timeout_add(25, self.check_scroll, pos)
        
        # scroll to first new tweet
        elif self.first_load or (offset > 0 and self.position == 0):
            height = self.gui.get_view_height()
            if offset > height:
                self.scroll_to = offset - height
                self.fix_scroll()
        
        if len(self.items) > 0:
            self.first_load = False
        
        self.after_loaded()
        self.load_history = False
        self.has_newitems = False
        self.fake_move(self.mouse_position)
        self.gui.update_app(True)
    
    def after_loaded(self):
        pass
    
    def on_scroll(self, view, event):
        # FIXME sometimes this still doesn't remove the menu
        self.current_scroll = self.scroll.get_vscrollbar().get_value()
        gobject.timeout_add(10, self.fake_move, self.mouse_position)
    
    def fix_scroll(self):
        if self.scroll_to != -1 and self.gui.mode == self.mode_type:
            self.scroll.get_vscrollbar().set_value(self.scroll_to)
            gobject.timeout_add(25, self.check_offset)
            self.scroll_to = -1
    
    def on_draw(self, *args):
        if self.is_rendering_history:
            if self.scroll.get_vscrollbar().get_value() == 0.0 \
               and self.scroll.get_vscrollbar().get_adjustment().get_upper() \
               > self.gui.get_view_height():
                
                return True
            
            else:
                self.is_rendering_history = False
                gobject.timeout_add(10, self.scroll.queue_draw)
                return True
    
    # Fakeman! Roger Buster!
    # This fixes an issue where the reply/favorite links wouldn't disapear if
    # the mouse left the view, plus it fixes tons of other issues
    def fake_move(self, pos, force=False):
        if not self.gui.is_shown:
            return False
        
        if not self.menu_no_fake_move or force:
            
            # Try to fix a crazy bug where this returns None...
            win = self.get_window()
            if win is None:
                gobject.idle_add(self.fake_move, pos)
                return False
            
            self.fake_mouse = True
            event = gtk.gdk.Event(gtk.gdk.MOTION_NOTIFY)
            event.window = win
            event.x = pos[0]
            event.y = pos[1]
            self.emit('motion_notify_event', event)
    
    def on_leave(self, view, event, *args):
        self.mouse_position = (-1.0, -1.0)
        self.fake_move(self.mouse_position)
    
    def on_move(self, view, event, *args):
        if not self.fake_mouse:
            self.mouse_position = (event.x, event.y)
        
        self.fake_mouse = False
    
    def on_key(self, view, event):
        # FIXME 65360 = Begin, it seems that the constant is broken, at least
        # on my keyboard
        i = gtk.keysyms
        if event.keyval in (i.Up, i.Down, i.Page_Up, i.Page_Down, i.End,
                            i.Begin, 65360, i.KP_Up, i.KP_Down, i.KP_Page_Up,
                            i.KP_Page_Down, i.KP_End, i.KP_Begin):
            
            self.on_scroll(None, None)
    
    # Double check for some stupid scrolling bugs with webkit
    def check_scroll(self, pos):
        self.scroll.get_vscrollbar().set_value(pos)
    
    def check_offset(self):
        offset = self.get_offset()
        height = self.gui.get_view_height()
        if offset > height:
            self.check_scroll(offset - height)
    
    
    # Time ---------------------------------------------------------------------
    # --------------------------------------------------------------------------
    def relative_time(self, date):
        delta = gmtime() - gmtime(date)
        
        if delta <= 1:
            return lang.html_about_second
        
        elif delta <= 45:
            return lang.html_second % delta
        
        elif delta <= 90:
            return lang.html_about_minute
        
        elif delta <= 60 * 45:
            return lang.html_minute % math.ceil(delta / 60.0)
        
        elif delta <= 60 * 60 * 1.5:
            return lang.html_about_hour
        
        elif delta <= 60 * 60 * 20:
            return lang.html_hour % math.ceil(delta / (60.0 * 60.0))
        
        elif delta <= 60 * 60 * 24 * 1.5:
            return lang.html_about_day
        
        elif delta <= 60 * 60 * 48:
            return lang.html_yesterday
        
        elif delta <= 60 * 60 * 72:
            return lang.html_day % math.ceil(delta / (60.0 * 60.0 * 24.0))
        
        else:
            return time.strftime(lang.html_exact, localtime(date))
    
    def absolute_time(self, date, message=False):
        delta = gmtime() - gmtime(date)
        date = localtime(date)
        if delta <= 60 * 60 * 24:
            return time.strftime(lang.html_time_message if message \
                                 else lang.html_time, date)
        
        else:
            return time.strftime(lang.html_time_day_message if message \
                                 else lang.html_time_day, date)
    
    
    # Helpers ------------------------------------------------------------------
    # --------------------------------------------------------------------------
    def is_new_timeline(self, item):
        self.new_timeline = item.id > self.new_items_id
        if self.new_timeline:
            self.count += 1
        
        if self.newest or self.init_id == 0:
            self.new_timeline = False
        
        if self.new_timeline:
            self.newest = True
    
    def is_new_avatar(self, num):
        if num < len(self.items) - 1:
            self.new_avatar = self.items[num + 1][0].id > self.new_items_id
        
        else:
            self.new_avatar = False
        
        if num > 0 and self.items[num - 1][0].id <= self.new_items_id:
            self.new_timeline = False
        
        if self.newest_avatar or self.init_id == 0:
            self.new_avatar = False
        
        if self.profile_mode:
            self.new_avatar = True
        
        if self.new_avatar:
            self.newest_avatar = True
    
    def is_protected(self, user):
        if hasattr(user, 'protected') and user.protected:
            return  ('<span class="protected" title="' \
                     + lang.html_protected + '"></span>') \
                     % lang.name(user.screen_name)
        
        else:
            return ''
    
    # Focus this view
    def focus_me(self):
        self.grab_focus()
        self.text.html_focus()
    
    # Get Image of an Item
    def get_image(self, num):
        return self.items[num][1]
    
    # Attribute helpers for new style Retweets
    def get_attr(self, item, attr, get_rt=False):
        item = self.items[item][0] if type(item) in (int, long) else item
        status = item.retweeted_status\
                 if hasattr(item, 'retweeted_status') and not get_rt else item
        
        return getattr(status, attr) if hasattr(status, attr) else None
    
    def get_user(self, item, get_rt=False):
        user = self.get_attr(item, 'user', get_rt = get_rt)
        return user if user is not None else self.get_attr(item, 'sender')
    
    def get_screen_name(self, item, get_rt=False):
        return self.get_user(item, get_rt = get_rt).screen_name
    
    def get_text(self, item):
        return self.get_attr(item, 'text')
    
    def get_source(self, item):
        return self.get_attr(item, 'source')
    
    def get_id(self, item):
        return self.get_attr(item, 'id')
    
    def get_reply_id(self, item):
        return self.get_attr(item, 'in_reply_to_status_id')
    
    def get_reply_user(self, item):
        return self.get_attr(item, 'in_reply_to_screen_name')
    
    def get_recipient(self, item):
        return self.get_attr(item, 'recipient')
    
    def get_sender(self, item):
        return self.get_attr(item, 'sender')
    
    def get_protected(self, item):
        user = self.get_user(item)
        return hasattr(user, 'protected') and user.protected

