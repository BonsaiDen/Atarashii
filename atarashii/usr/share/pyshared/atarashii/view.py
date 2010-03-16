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


# Basic HTML View --------------------------------------------------------------
# ------------------------------------------------------------------------------
import gobject
import webkit
import gtk

import calendar
import math
import time
import webbrowser

import formatter
from utils import unescape, compare_sub

from lang import lang
from constants import HTML_STATE_NONE, HTML_UNSET_ID, \
                      RETWEET_NEW, RETWEET_OLD, UNSET_TEXT, UNSET_ID_NUM


# Watch out! This is one giant "Is this OK mommy?" hackery by the kittens!
# You've been warned...
# ------------------------------------------------------------------------------
class HTMLView(webkit.WebView):
    def __init__(self, main, gui, scroll):
        self.main = main
        self.gui = gui
        
        webkit.WebView.__init__(self)
        self.connect("navigation-requested", self.open_link)
        self.connect("load-finished", self.loaded)
        self.connect("button-release-event", self.gui.text.html_focus)
        self.connect("button-press-event", self.on_button)
        self.connect("populate-popup", self.on_popup)
        
        # Fix CSS hover stuff
        self.mouse_position = -1.0
        self.connect("motion-notify-event", self.on_move)
        self.connect("leave-notify-event", self.on_leave)
        self.last_scroll = 0
        self.connect("scroll-event", self.on_scroll)
        
        self.scroll = scroll
        self.set_maintains_back_forward_list(False)
        self.count = 0
        self.formatter = formatter.Formatter()
        self.get_latest = None
        self.item_count = 20
        self.get_item_count = None
        self.set_item_count = None
        
        self.lang_loading = ""
        self.lang_load = ""
        self.lang_empty = ""
        
        self.init(True)
    
    
    # Initiate a empty timeline ------------------------------------------------
    # --------------------------------------------------------------------------
    def init(self, splash = False):
        self.items = []
        self.update_list = []
        self.history_list = []
        self.position = 0
        self.offset_count = 0
        self.history_loaded = False
        self.history_position = HTML_UNSET_ID
        self.history_count = 0
        self.first_load = True
        self.newest_id = HTML_UNSET_ID
        self.has_newitems = False
        self.load_history = False
        self.load_history_id = HTML_UNSET_ID
        self.load_state = HTML_UNSET_ID
        self.init_id = HTML_UNSET_ID
        self.last_id = HTML_UNSET_ID
        self.count = 0
        
        if splash:
            self.splash()
    
    
    # Render the actual HTML ---------------------------------------------------
    # --------------------------------------------------------------------------
    def init_render(self):
        self.position = self.scroll.get_vscrollbar().get_value()
        self.items.sort(compare_sub)
        self.count = 0
        
        # Set the latest tweet for reloading on startup
        if len(self.items) > 0:
            itemid = len(self.items) - self.item_count
            if itemid < 0:
                itemid = 0
            
            setting = self.first_setting + self.main.username
            self.main.settings[setting] = self.items[itemid][0].id - 1
        
        # Newest Stuff
        self.newest = False
        self.newest_avatar = False
        self.new_timline = False
        if self.newest_id == HTML_UNSET_ID:
            self.newest_id = self.init_id
    
    def render(self):
        self.init_render()
        self.last_name = ""
        self.last_recipient = ""
        self.last_highlight = False
        self.last_mentioned = False
        
        # Do the rendering!
        self.renderitems = []
        for num, obj in enumerate(self.items):
            item, img = obj
            self.is_new_timeline(item)
            html = self.render_item(num, item, img)
            
            # Close Newest Container
            if item.id == self.newest_id:
                html = '</div>' + html
            
            self.renderitems.insert(0, html)
        
        # Render
        self.set_html(self.renderitems)
    
    
    # HTML Helpers -------------------------------------------------------------
    def start(self):
        self.scroll.get_vscrollbar().set_value(0)
        self.offset_count = 0
        self.render_html("""
            <body class="unloaded" ondragstart="return false">
                <div class="loading"><img src="file://%s" /><br/><b>%s</b></div>
            </body>""" % (self.main.get_image(), self.lang_loading))
    
    def splash(self):
        self.scroll.get_vscrollbar().set_value(0)
        self.offset_count = 0
        self.render_html("""
            <body class="unloaded" ondragstart="return false">
                <div class="loading"><img src="file://%s" /><br/><b>%s</b></div>
            </body>""" % (self.main.get_image(), lang.html_welcome))
    
    def render_html(self, html):
        self.load_string("""
        <html>
        <head>
        <meta content="text/html; charset=UTF-8" http-equiv="content-type"/>
        <link rel="stylesheet" type="text/css" media="screen" href="file://%s"/>
        </head>
        %s
        </html>""" % (self.main.get_resource("atarashii.css"), html),
                        "text/html", "UTF-8", "file:///")
    
    def set_html(self, renderitems):
        self.main.gui.set_app_title()
        if len(self.items) > 0:
            self.render_html("""
                <body ondragstart="return false">
                    <div><div id="newcontainer">%s</div>
                    <div class="loadmore"><a href="more:%d"><b>%s</b></a></div>
                </body>""" % ("".join(renderitems),
                                self.items[0][0].id, self.lang_load))
        
        elif self.main.login_status:
            self.render_html("""
                <body class="unloaded" ondragstart="return false">
                    <div class="loading"><b>%s</b></div>
                </body>""" % self.lang_empty)
    
    # The big magic spacer inserted... trust me it's really magic that this
    # thin does work at all...
    def insert_spacer(self, item, user, highlight, mentioned,
                    next_highlight = False, force = False):
        
        spacer = "foo"
        if item.id > self.init_id:
            # Name change
            if self.last_name != user.screen_name or self.new_timeline or force:
                spacer = "1" # Dark Gray
            
            else:
                # More @username
                if highlight:
                    if not self.last_highlight:
                        spacer = "1" # Dark Gray
                    
                    else:
                        spacer = "6" # Normal/Dark Blue
                
                # More mentions
                elif mentioned:
                    if not self.last_mentioned:
                        spacer = "1" # Dark Gray
                    
                    else:
                        spacer = "5" # Yellow
                
                # Just more normal tweets
                else:
                    if next_highlight and self.last_highlight:
                        spacer = "1" # Dark Gray
                    
                    elif next and self.last_mentioned:
                        spacer = "1" # Normal Gray
                    
                    elif self.last_highlight:
                        spacer = "1" # Dark Gray
                    
                    else:
                        spacer = "4" # Dark/Normal Blue
        
        # Old Tweets
        else:
            # Name change
            if self.last_name != user.screen_name or self.new_timeline or force:
                spacer = "" # Normal Gray
            
            else:
                # More @username
                if highlight:
                    if not self.last_highlight:
                        spacer = "" # Normal Gray
                    
                    else:
                        spacer = "7" # White/Light Blue
                
                # More mentions
                elif mentioned:
                    if not self.last_mentioned:
                        spacer = "" # Dark Gray
                    
                    else:
                        spacer = "8" # Yellow
                
                # Just more normal tweets
                else:
                    if next_highlight and self.last_highlight:
                        spacer = "" # Normal Gray
                    
                    elif next and self.last_mentioned:
                        spacer = "" # Normal Gray
                    
                    elif self.last_highlight:
                        spacer = "" # Normal Gray
                    
                    else:
                        spacer = "2" # Light Blue/White
        
        return '<div class="spacer%s"></div>' % spacer
    
    
    # History / Read Button ----------------------------------------------------
    # --------------------------------------------------------------------------
    def clear(self):
        self.history_loaded = False
        self.items = self.items[self.history_count:]
        self.set_item_count(self.get_item_count() - self.history_count)
        self.history_count = 0
        self.main.gui.history_button.set_sensitive(False)
        self.render()
    
    def read(self):
        if self.init_id != self.get_latest():
            self.main.gui.read_button.set_sensitive(False)
            self.init_id = self.get_latest()
            if not self.history_loaded:
                pos = len(self.items) - self.item_count
                if pos < 0:
                    pos = 0
                
                self.items = self.items[pos:]
            
            self.render()
    
    
    # Fix scrolling isses on page load -----------------------------------------
    # --------------------------------------------------------------------------
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
            gobject.timeout_add(25, lambda: self.check_scroll(pos))
        
        # scroll to first new tweet
        elif self.first_load or (offset > 0 and self.position == 0):
            height = self.gui.get_height(self)
            if offset > height:
                self.scroll.get_vscrollbar().set_value(offset - height)
                gobject.timeout_add(25, self.check_offset)
        
        if len(self.items) > 0:
            self.first_load = False
        
        self.load_history = False
        self.has_newitems = False
        self.fake_click()
    
    # Fakeman! Roger Buster!
    # This fixes an issue where the reply/favorite links wouldn't disapear if
    # the mouse left the view
    def fake_click(self):
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
        gobject.timeout_add(10, lambda *args: self.fake_click())

    # Double check for some stupid scrolling bugs with webkit
    def check_scroll(self, pos):
        self.scroll.get_vscrollbar().set_value(pos)
    
    def check_offset(self):
        offset = self.get_offset()
        height = self.gui.get_height(self)
        if offset > height:
            self.scroll.get_vscrollbar().set_value(offset - height)
    
    
    # Item management ----------------------------------------------------------
    # --------------------------------------------------------------------------
    def push_updates(self):
        while len(self.update_list) > 0:
            self.add(self.update_list.pop(0))
        
        while len(self.history_list) > 0:
            self.add(self.history_list.pop(0), True)
        
        self.render()
    
    def add(self, item, append = False):        
        # Don't add items with the same ID twice
        if not item[0].id in [i[0].id for i in self.items]:
            if append:
                self.items.insert(0, item)
            
            else:
                self.items.append(item)
            
            self.has_newitems = True
            if len(self.items) > self.main.max_tweet_count:
                self.items.pop(0)
    
    def remove(self, item_id):
        remove_item_id = UNSET_ID_NUM
        for i in range(len(self.items)):
            if self.get_id(self.items[i][0]) == item_id:
                remove_item_id = i
                break
        
        if remove_item_id != UNSET_ID_NUM:
            self.items.pop(remove_item_id)
            self.render()
    
    def favorite(self, item_id, mode):
        fav_item_id = UNSET_ID_NUM
        for i in range(len(self.items)):
            item = self.items[i][0]
            if self.get_id(item) == item_id:
                if hasattr(item, "retweeted_status"):
                    self.items[i][0].retweeted_status.favorited = mode
                
                else:
                    self.items[i][0].favorited = mode
                
                self.render()
                break
    
    
    # Popup Menu ---------------------------------------------------------------
    # --------------------------------------------------------------------------
    def on_popup(self, view, menu, *args): # Kill of the original context menu!
        menu.hide()
        menu.cancel()
        menu.destroy()
        return True
    
    # Let's create our own nice little popup :)
    def on_button(self, view, event, *args):
        if event.button == 3:
            # Calculate on which item the user clicked
            item_id, link = self.get_clicked_item(self.get_sizes(event), event)
            if item_id == -1:
                return False
            
            item = self.items[item_id][0]
            
            # Create Menu
            menu = gtk.Menu()
            self.create_menu(menu, item, link)
            if len(menu.get_children()) == 0:
                return False
            
            menu.show_all()
            menu.connect("hide", self.on_popup_close)
            
            # This makes the menu popup just besides the mouse pointer
            # It fixes an issues were the user would release the mouse button
            # and trigger an menu item without wanting to do so
            def position(*args):
                return (int(event.x_root), int(event.y_root), True)
            
            menu.attach_to_widget(self, lambda *args: False)
            menu.popup(None, None, position, event.button, event.get_time())
            return True
    
    def add_menu_link(self, menu, name, callback):
        item = gtk.MenuItem()
        item.set_label(name)
        item.connect('activate', callback)
        menu.append(item)
    
    def add_menu_separator(self, menu):
        item = gtk.SeparatorMenuItem()
        menu.append(item)
    
    def on_popup_close(self, *args):
        self.gui.text.html_focus()
    
    
    # Get a Tweet based on a button press --------------------------------------
    def get_clicked_item(self, items, event):
        if items == None:
            return -1
        
        # Get Positions and Link
        items, link = items.split("|")
        if link == "undefined":
            link = None
        
        items = items.split(";")
        mouse_y = event.y + self.scroll.get_vscrollbar().get_value()
        item_num = -1
        last_pos = 0
        for i in items:
            data = i.split(",")
            if len(data) > 1:
                pos = int(data[1])
                if mouse_y >= last_pos and mouse_y < pos:
                    item_num = int(data[0])
                    break
                
                last_pos = pos
        
        return item_num, link
    
    # Run some crazy javascript in order to calculate all the positioning
    def get_sizes(self, event):
        try:
            self.execute_script('''
            var sizes = [];
            var items = document.getElementsByClassName("viewitem");
            var pos = 0;
            for (var i = 0; i < items.length; i++) {
                var item = items[i];
                pos += item.offsetHeight;
                sizes.push([item.getAttribute("id"), pos])
                pos += 2;
                delete item;
            };
            delete pos;
            delete items;
            var link = document.elementFromPoint(%d, %d);
            document.title = sizes.join(";") + "|" + 
            (link.href != undefined ? link.href : link.parentNode.href);
            delete link;
            delete sizes;''' % (event.x, event.y))
            title = self.get_main_frame().get_title()
            return title
            
        except:
            return None
    
    
    # Handle the opening of Links ----------------------------------------------
    # --------------------------------------------------------------------------
    def context_link(self, uri, extra = None):
        self.open_link(None, None, None, uri, extra)
    
    def open_link(self, view, frame, req, uri = None, extra = None):
        # Get URI
        if uri == None:
            uri = req.get_uri()
        
        # Local links
        if uri.startswith("file:///"):
            return False
        
        # Load history
        if uri.startswith("more:"):
            if not self.main.is_loading_history:
                self.load_history_id = int(uri.split(":")[1]) - 1
                if self.load_history_id != HTML_UNSET_ID:
                    self.main.is_loading_history = True
                    self.gui.show_progress()
                    gobject.idle_add(lambda: self.main.gui.update_status(True))
                    self.main.gui.text.html_focus()
        
        # Replies
        elif uri.startswith("reply:"):
            ref, self.main.reply_user, self.main.reply_id, num = uri.split(":")
            num = int(num)
            if extra != None:
                self.main.reply_text = unescape(self.get_text(extra))
            
            elif num != -1:
                self.main.reply_text = unescape(self.get_text(num))
            
            else:
                self.main.reply_text = UNSET_TEXT
            
            self.main.gui.text.reply()
            self.main.gui.text.html_focus()
        
        # Send a message
        elif uri.startswith("message:"):
            ref, self.main.message_user, \
                self.main.message_id, num = uri.split(":")
            
            num = int(num)
            if extra != None:
                self.main.message_text = unescape(self.get_text(extra))
            
            elif num != -1:
                self.main.message_text = unescape(self.get_text(num))
            
            else:
                self.main.message_text = UNSET_TEXT
            
            self.main.gui.text.message()
            self.main.gui.text.html_focus()
        
        # Retweet someone
        elif uri.startswith("retweet:"):
            ref, ttype = uri.split(":")
            tweet_id = self.get_id(extra)
            name = self.get_user(extra).screen_name
            
            # Which style?
            if int(ttype) == RETWEET_NEW:
                self.main.retweet(name, tweet_id, True)
            
            elif int(ttype) == RETWEET_OLD:
                self.main.retweet_text = unescape(self.get_text(extra))
                self.main.retweet_user = name
                self.main.gui.text.retweet()
                self.main.gui.text.html_focus()
        
        # Delete
        elif uri.startswith("delete:"):
            ref, dtype, item_id = uri.split(":")
            item_id = int(item_id)
            text = unescape(self.get_text(extra))
            
            def delete_tweet():
                self.main.delete(tweet_id = item_id)
            
            def delete_message():
                self.main.delete(message_id = item_id)
            
            # Ask
            if dtype == "t":
                gobject.idle_add(lambda: self.main.gui.ask_for_delete_tweet(
                                         text,
                                         delete_tweet,
                                         None))
            
            elif dtype == "m":
                gobject.idle_add(lambda: self.main.gui.ask_for_delete_message(
                                         text,
                                         delete_message,
                                         None))
        
        # Favorite
        elif uri.startswith("fav:"):
            ref, item_id = uri.split(":")
            self.favorite(int(item_id), True)
        
        # Un-Favorite
        elif uri.startswith("unfav:"):
            ref, item_id, = uri.split(":")
            self.favorite(int(item_id), False)
        
        # Regular links
        else:
            webbrowser.open(self.get_link_type(uri)[1])
        
        return True
    
    def get_link_type(self, uri):
        if uri == None:
            return None, None, None
    
        if uri.startswith("profile:"):
            return "profile", uri[8:], uri
        
        elif uri.startswith("user:"):
            return "user", uri[5:], uri
        
        elif uri.startswith("source:"):
            return "source", uri[7:], uri
        
        elif uri.startswith("status:"):
            return "status", uri[7:], uri
        
        elif uri.startswith("tag:"):
            return "tag", uri[4:], uri
        
        else:
            return "link", uri, uri
    
    def copy_link(self, url):
        display = gtk.gdk.display_manager_get().get_default_display()
        clipboard = gtk.Clipboard(display, "CLIPBOARD")
        clipboard.set_text(url)
    
    
    # Helpers ------------------------------------------------------------------
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
    
    
    # Checks for new Tweets
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
    
