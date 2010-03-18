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
import gobject
import gtk

import calendar
import time
import math

from language import LANG as lang

class ViewHelpers:
    def __init__(self):
        pass
    
    # Scrolling ----------------------------------------------------------------
    # --------------------------------------------------------------------------
    def get_height(self):
        size = self.get_allocation()
        return size[3] - size[0]
    
    def get_offset(self):
        try:
            self.execute_script(
                '''document.title=
                    document.getElementById("newcontainer").offsetHeight;''')
            return int(self.get_main_frame().get_title())
        
        except:
            return 0
    
    def loaded(self, *args):
        if len(self.items) > 0 and self.has_newitems and not self.load_history:
            offset = self.get_offset()
        
        else:
            offset = 0
        
        # Re-scroll
        if not self.first_load and self.position > 0:
            pos = self.position + offset
            self.check_scroll(pos)
            gobject.timeout_add(25, self.check_scroll, pos)
        
        # scroll to first new tweet
        elif self.first_load or (offset > 0 and self.position == 0):
            height = self.get_height()
            if offset > height:
                self.scroll_to = offset - height
                self.fix_scroll()
        
        if len(self.items) > 0:
            self.first_load = False
        
        self.load_history = False
        self.has_newitems = False
        self.fake_click()
    
    # Fakeman! Roger Buster!
    # This fixes an issue where the reply/favorite links wouldn't disapear if
    # the mouse left the view
    def fake_click(self):
        # Don't steal focus from the text box
        if self.gui.text.has_focus:
            self.give_text_focus = True      
        
        event = gtk.gdk.Event(gtk.gdk.BUTTON_PRESS)
        event.x = 0.0
        event.y = self.mouse_position
        event.button = 1
        self.emit("button_press_event", event)
        
    
    def on_leave(self, view, event, *args):
        self.mouse_position = -1.0
        self.fake_click()
    
    def on_move(self, view, event, *args):
        self.mouse_position = event.y
    
    def on_scroll(self, view, event, *args):
        gobject.timeout_add(10, self.fake_click)
        
    def fix_scroll(self):
        if self.scroll_to != -1 and self.main.gui.mode == self.mode_type:
            self.scroll.get_vscrollbar().set_value(self.scroll_to)
            gobject.timeout_add(25, self.check_offset)
            self.scroll_to = -1
    
    # Double check for some stupid scrolling bugs with webkit
    def check_scroll(self, pos):
        self.scroll.get_vscrollbar().set_value(pos)
    
    def check_offset(self):
        offset = self.get_offset()
        height = self.get_height()
        if offset > height:
            self.scroll.get_vscrollbar().set_value(offset - height)
    
    
    # Time ---------------------------------------------------------------------
    # --------------------------------------------------------------------------
    def relative_time(self, date):
        delta = long(calendar.timegm(time.gmtime())) - \
                long(calendar.timegm(date.timetuple()))
        
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
            date = time.localtime(calendar.timegm(date.timetuple()))
            return time.strftime(lang.html_exact, date)
    
    def absolute_time(self, date):
        delta = long(calendar.timegm(time.gmtime())) - \
                long(calendar.timegm(date.timetuple()))
        
        date = time.localtime(calendar.timegm(date.timetuple()))
        if delta <= 60 * 60 * 24:
            return time.strftime(lang.html_time, date)
        
        else:
            return time.strftime(lang.html_time_day, date)
    
    
    # Helpers ------------------------------------------------------------------
    # --------------------------------------------------------------------------
    def is_new_timeline(self, item):
        self.new_timeline = item.id > self.init_id
        if self.new_timeline:
            self.count += 1
        
        if self.newest or self.init_id == 0:
            self.new_timeline = False
        
        if self.new_timeline:
            self.newest = True
    
    def is_new_avatar(self, num):
        if num < len(self.items) - 1:
            self.new_avatar = self.items[num + 1][0].id > self.init_id
        
        else:
            self.new_avatar = False
        
        if num > 0 and self.items[num - 1][0].id <= self.init_id:
            self.new_timeline = False
        
        if self.newest_avatar or self.init_id == 0:
            self.new_avatar = False
        
        if self.new_avatar:
            self.newest_avatar = True
    
    def is_protected(self, user):
        if hasattr(user, "protected") and user.protected:
            return  ('<span class="protected" title="' + \
                     lang.html_protected + '"></span>') % \
                     lang.name(user.screen_name)
        
        else:
            return ''
    
    # Focus this view
    def focus_me(self):
        self.grab_focus()
        self.gui.text.html_focus()
    
    # Attribute helpers for new style Retweets
    def get_attr(self, item, attr):
        item = self.items[item][0] if type(item) in (int, long) else item
        return (item.retweeted_status if \
                hasattr(item, "retweeted_status") else item).__dict__[attr]
    
    def get_user(self, item):
        return self.get_attr(item, "user")
    
    def get_text(self, item):
        return self.get_attr(item, "text")
        
    def get_source(self, item):
        return self.get_attr(item, "source")
    
    def get_id(self, item):
        return self.get_attr(item, "id")
    
    def get_recipient(self, item):
        return self.get_attr(item, "recipient")
    
    def get_sender(self, item):
        return self.get_attr(item, "sender")
    
    def get_protected(self, item):
        user = self.get_user(item)
        return hasattr(user, "protected") and user.protected

