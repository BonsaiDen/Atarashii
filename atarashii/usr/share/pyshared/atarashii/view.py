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

import calendar
import math
import time
import webbrowser

import formatter
from lang import lang
from constants import HTML_STATE_NONE, HTML_UNSET_ID, HTML_STATE_START, \
                      HTML_STATE_SPLASH, HTML_STATE_RENDER, RETWEET_ASK, \
                      RETWEET_NEW, RETWEET_OLD


class HTMLView(webkit.WebView):
    def __init__(self, main, gui, scroll):
        self.main = main
        self.gui = gui
        
        webkit.WebView.__init__(self)
        self.connect("navigation-requested", self.open_link)
        self.connect("load-finished", self.loaded)
        self.connect("load-started", self.on_loading)
        self.connect("focus-in-event", self.gui.text.html_focus)
        self.scroll = scroll
        self.set_maintains_back_forward_list(False)
        self.mode = HTML_STATE_NONE
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
        self.is_rendering = False
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
        self.newitems = False
        self.load_history = False
        self.load_history_id = HTML_UNSET_ID
        self.loaded = HTML_UNSET_ID
        self.init_id = HTML_UNSET_ID
        self.last_id = HTML_UNSET_ID
        self.count = 0
        
        if splash:
            self.splash()
    
    
    # Loading HTML -------------------------------------------------------------
    # --------------------------------------------------------------------------
    def start(self):
        self.offset_count = 0
        self.render_html("""
            <body class="unloaded">
                <div class="loading"><img src="file://%s" /><br/><b>%s</b></div>
            </body>""" % (self.main.get_image(), self.lang_loading),
            HTML_STATE_START)
    
    def splash(self):
        self.offset_count = 0
        self.render_html("""
            <body class="unloaded">
                <div class="loading"><img src="file://%s" /><br/><b>%s</b></div>
            </body>""" % (self.main.get_image(), lang.html_welcome),
            HTML_STATE_SPLASH)
    
    
    # Render the actual HTML ---------------------------------------------------
    # --------------------------------------------------------------------------
    def render_html(self, html, mode):
        self.mode = mode
        self.is_rendering = True
        self.load_string("""
        <html>
        <head>
        <meta content="text/html; charset=UTF-8" http-equiv="content-type"/>
        <link rel="stylesheet" type="text/css" media="screen" href="file://%s"/>
        </head>
        %s
        </html>""" % (self.main.get_resource("atarashii.css"), html),
                        "text/html", "UTF-8", "file:///main/")
    
    def set_html(self, renderitems):
        self.main.gui.set_app_title()
        if len(self.items) > 0:
            self.render_html("""
                <body>
                    <div><div id="newcontainer">%s</div>
                    <div class="loadmore"><a href="more:%d"><b>%s</b></a></div>
                </body>""" % ("".join(renderitems),
                                self.items[0][0].id, self.lang_load),
                                HTML_STATE_RENDER)
        
        else:
            self.render_html("""
                <body class="unloaded">
                    <div class="loading"><b>%s</b></div>
                </body>""" % self.lang_empty, HTML_STATE_RENDER)
    
    def insert_spacer(self, item, user, highlight, mentioned, message = False, 
                    next = False, force = False):
        
        spacer = "foo"
        if item.id > self.init_id:
            # Name change
            if self.lastname != user.screen_name or self.new_timeline or force:
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
                    if next and self.last_highlight:
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
            if self.lastname != user.screen_name or self.new_timeline or force:
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
                    if next and self.last_highlight:
                        spacer = "" # Normal Gray
                    
                    elif next and self.last_mentioned:
                        spacer = "" # Normal Gray
                    
                    elif self.last_highlight:
                        spacer = "" # Normal Gray
                    
                    else:
                        spacer = "2" # Light Blue/White
        
        return '<div class="spacer%s"></div>' % spacer
    
    
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
        self.is_rendering = False
        if len(self.items) > 0 and self.newitems and not self.load_history:
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
        self.newitems = False
    
    
    # Double check for some stupid scrolling bugs with webkit
    def check_scroll(self, pos):
        self.scroll.get_vscrollbar().set_value(pos)
    
    def check_offset(self):
        offset = self.get_offset()
        height = self.gui.get_height(self)
        if offset > height:
            self.scroll.get_vscrollbar().set_value(offset - height)
    
    
    # Fix Reloading
    def on_loading(self, *args):
        if not self.is_rendering:
            if self.mode == HTML_STATE_RENDER:
                self.render()
            
            elif self.mode == HTML_STATE_START:
                self.start()
            
            elif self.mode == HTML_STATE_SPLASH:
                self.splash()
            
            return True
    
    
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
    
    
    # Add Items ----------------------------------------------------------------
    # --------------------------------------------------------------------------
    def push_updates(self):
        while len(self.update_list) > 0:
            self.add(self.update_list.pop(0))
        
        while len(self.history_list) > 0:
            self.add(self.history_list.pop(0), True)
        
        self.render()
    
    
    # Add items to the internal List
    def add(self, item, append = False):        
        # Don't add items with the same ID twice
        if not item[0].id in [i[0].id for i in self.items]:
            if append:
                self.items.insert(0, item)
            
            else:
                self.items.append(item)
            
            self.newitems = True
            if len(self.items) > self.main.max_tweet_count:
                self.items.pop(0)
    
    def compare(self, x, y):
        if x[0].id > y[0].id:
            return 1
        
        elif x[0].id < y[0].id:
            return -1
        
        else:
            return 0
    
    
    # Setup rendering ----------------------------------------------------------
    # --------------------------------------------------------------------------
    def init_render(self):
        self.position = self.scroll.get_vscrollbar().get_value()
        self.items.sort(self.compare)
        self.count = 0
        
        # Set the latest tweet for reloading on startup
        if len(self.items) > 0:
            itemid = len(self.items) - self.item_count
            if itemid < 0:
                itemid = 0
            
            setting = self.first_setting + self.main.username
            self.main.settings[setting] = self.items[itemid][0].id - 1
        
        # Newest Stuff
        if self.newest_id == HTML_UNSET_ID:
            self.newest_id = self.init_id
        
        # Newest Stuff
        self.newest = False
        self.newest_avatar = False
        self.new_timline = False
    
    
    # Render the Timeline ------------------------------------------------------
    # --------------------------------------------------------------------------
    def render(self):
        self.init_render()
        self.lastname = ""
        self.lastrecipient = ""
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
    
    
    # Handle the opening of links ----------------------------------------------
    # --------------------------------------------------------------------------
    def open_link(self, view, frame, req):
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
            foo, self.main.reply_user, self.main.reply_id, num = uri.split(":")
            self.main.gui.text.reply()
            self.main.gui.text.html_focus()
        
        # Send a message
        elif uri.startswith("message:"):
            o, self.main.message_user, self.main.message_id, num = uri.split(":")
            self.main.message_text = self.unescape(self.items[int(num)][0].text)
            self.main.gui.text.message()
            self.main.gui.text.html_focus()
        
        # Retweet someone
        elif uri.startswith("retweet:"):
            foo, num, tweetid = uri.split(":")
            num, tweetid = int(num), long(tweetid)
            name = self.get_user(num).screen_name
            
            def old_retweet():
                self.main.retweet_text = self.unescape(self.get_text(num))
                self.main.retweet_user = name
                self.main.gui.text.retweet()
                self.main.gui.text.html_focus()
            
            
            def new_retweet():
                self.main.retweet(name, tweetid)
            
            # Which style?
            rt_temp = self.main.settings["retweets"]
            if name.lower() == self.main.username.lower():
                rt_temp = RETWEET_OLD
            
            if rt_temp == RETWEET_ASK:
                self.main.gui.ask_for_retweet(name, new_retweet, old_retweet)
            
            elif rt_temp == RETWEET_NEW:
                new_retweet()
            
            elif rt_temp == RETWEET_OLD:
                old_retweet()
        
        # Regular links
        else:
            webbrowser.open(uri)
        
        return True
    
    
    # Unescape chars
    def unescape(self, text):
        ent = {
            "&": "&amp;",
            '"': "&quot;",
            "'": "&apos;",
            ">": "&gt;",
            "<": "&lt;"
        }
        for key, value in ent.iteritems():
            text = text.replace(value, key)
        
        return text

