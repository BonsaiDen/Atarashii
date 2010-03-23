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
import pygtk
pygtk.require('2.0')
import gtk
import gobject

import webkit
import webbrowser

import formatter

from utils import unescape
from view_menu import ViewMenu
from view_helpers import ViewHelpers
from view_html import ViewHTML

from constants import ST_HISTORY
from constants import HTML_UNSET_ID, RETWEET_NEW, RETWEET_OLD, UNSET_TEXT, \
                      UNSET_ID_NUM


# Watch out! This is one giant "Is this OK mommy?" hackery by the kittens!
# You've been warned...
# ------------------------------------------------------------------------------
class HTMLView(webkit.WebView, ViewMenu, ViewHelpers, ViewHTML):
    def __init__(self, main, gui, scroll, mode):
        self.main = main
        self.gui = gui
        self.mode_type = mode
        
        webkit.WebView.__init__(self)
        self.connect('navigation-requested', self.open_link)
        self.connect('notify::load-status', self.loaded)
        self.connect('button-release-event', self.gui.text.html_focus)
        self.connect('button-press-event', self.on_button)
        self.connect('populate-popup', self.on_popup)
        self.popup_open = False
        
        # Fix CSS hover stuff
        self.mouse_position = (-1.0, -1.0)
        self.fake_mouse = False
        self.connect('motion-notify-event', self.on_move)
        self.connect('leave-notify-event', self.on_leave)
        self.last_scroll = 0
        self.connect('scroll-event', self.on_scroll)
        self.connect('key-release-event', self.on_key)
        
        # Better link tooltips
        self.last_hovered_link = ''
        self.connect('hovering-over-link', self.on_link_hover)
        self.connect('query-tooltip', self.on_tooltip)
        
        # Tooltip
        gtb = gtk.Builder()
        gtb.add_from_file(self.main.get_resource('avatar.glade'))
        self.tooltip = gtb.get_object('tooltip')
        self.tooltip_label = gtb.get_object('label')
        self.tooltip_img = gtb.get_object('image')
        self.tooltip_img_file = None
        self.tooltip_user = None
        self.tooltip.show_all()
        self.tooltip_window = None
        self.scrolled = True
                
        # Other Stuff
        self.give_text_focus = False
        self.scroll = scroll
        self.set_maintains_back_forward_list(False)
        self.count = 0
        self.formatter = formatter.Formatter()
        self.item_count = 20
                
        self.lang_loading = ''
        self.lang_load = ''
        self.lang_empty = ''
        
        self.scroll_to = -1
        self.init(True)
        
        # Disable everything we can, in order to fix the memleak.
        off = ['enable_plugins', 'enable_offline_web_application_cache',
               'enable_html5_local_storage', 'enable_html5_database',
               'enable_developer_extras', 'enable_private_browsing',
               'enable_spell_checking', 'enable_xss_auditor']
        
        settings = self.get_settings()
        for i in off:
            settings.set_property(i, False)
    
    
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
    
    
    # History / Read Button ----------------------------------------------------
    # --------------------------------------------------------------------------
    def save_first(self):
        if len(self.items) > 0:
            itemid = len(self.items) - self.item_count
            if itemid < 0:
                itemid = 0
            
            setting = self.first_setting + self.main.username
            self.main.settings[setting] = self.items[itemid][0].id - 1
    
    def clear(self):
        self.history_loaded = False
        self.items = self.items[self.history_count:]
        self.set_item_count(self.get_item_count() - self.history_count)
        self.history_count = 0
        self.gui.set_refresh_update(True)
        self.render()
    
    def read(self):
        if self.init_id != self.get_latest():
            self.init_id = self.get_latest()
            self.main.gui.set_refresh_update(False, True)
            if not self.history_loaded:
                pos = len(self.items) - self.item_count
                if pos < 0:
                    pos = 0
                
                self.items = self.items[pos:]
            
            self.render()
            gobject.idle_add(self.main.save_settings, True)
    
    
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
        for i in range(len(self.items)):
            item = self.items[i][0]
            if self.get_id(item) == item_id:
                if hasattr(item, 'retweeted_status'):
                    self.items[i][0].retweeted_status.favorited = mode
                
                else:
                    self.items[i][0].favorited = mode
                
                self.render()
                break
    
    
    # Handle the opening of Links ----------------------------------------------
    # --------------------------------------------------------------------------
    def context_link(self, menu, uri, extra = None):
        self.open_link(None, None, None, uri, extra)
    
    def open_link(self, view, frame, req, uri = None, extra = None):
        # Get URI
        if uri == None:
            uri = req.get_uri()
        
        # Local links
        if uri.startswith('file:///'):
            return False
        
        # Load history
        if uri.startswith('more:'):
            if not self.main.status(ST_HISTORY):
                self.load_history_id = int(uri.split(':')[1]) - 1
                if self.load_history_id != HTML_UNSET_ID:
                    self.main.set_status(ST_HISTORY)
                    self.gui.show_progress()
                    gobject.idle_add(self.main.gui.update_status, True)
                    self.main.gui.text.html_focus()
        
        # Replies
        elif uri.startswith('reply:') or uri.startswith('qreply:'):
            self.main.reply_user, self.main.reply_id, num = uri.split(':')[1:]
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
        elif uri.startswith('message:') or uri.startswith('qmessage:'):
            self.main.message_user, \
            self.main.message_id, num = uri.split(':')[1:]
            
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
        elif uri.startswith('retweet:'):
            ttype = uri.split(':')[1]
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
        elif uri.startswith('delete:'):
            dtype, item_id = uri.split(':')[1:]
            item_id = int(item_id)
            text = unescape(self.get_text(extra))

            
            def delete_tweet():
                self.main.delete(tweet_id = item_id)
            
            def delete_message():
                self.main.delete(message_id = item_id)
            
            # Ask
            if dtype == 't':
                gobject.idle_add(self.main.gui.ask_for_delete_tweet,
                                 text,
                                 delete_tweet,
                                 None)
            
            elif dtype == 'm':
                gobject.idle_add(self.main.gui.ask_for_delete_message,
                                 text,
                                 delete_message,
                                 None)
        
        # Favorite
        elif uri.startswith('fav:'):
            name, item_id = uri.split(':')[1:]
            gobject.idle_add(self.main.favorite, int(item_id), True, name)
        
        # Un-Favorite
        elif uri.startswith('unfav:'):
            name, item_id, = uri.split(':')[1:]
            gobject.idle_add(self.main.favorite, int(item_id), False, name)
        
        # Edit
        elif uri.startswith('edit:'):
            self.main.edit_text = unescape(self.get_text(extra))
            self.main.edit_reply_id = self.get_reply_id(extra) or UNSET_ID_NUM
            self.main.edit_reply_user = self.get_reply_user(extra) or UNSET_TEXT
            self.main.edit_id = self.get_id(extra)
            self.main.gui.text.edit()
            self.main.gui.text.html_focus()
        
        # Regular links
        else:
            webbrowser.open(self.get_link_type(uri)[1])
        
        # Don't close the textbox
        if self.give_text_focus:
            gobject.idle_add(self.gui.text.grab_focus)
        
        return True
    
    def get_link_type(self, uri):
        if uri == None:
            return None, None, None
        
        # Link types
        types = ['profile', 'rprofile', 'user', 'source', 'status', 'tag',
                 'fav', 'unfav', 'qreply', 'qmessage', 'edit']
        
        # Generic cases
        for i in types:
            tag = i + ':'
            if uri.startswith(tag):
                return i, uri[len(tag):], uri
        
        # Special cases
        if uri.startswith('avatar:'):
            stuff = uri[7:]
            return 'avatar', stuff[stuff.find(':') + 1:], uri
        
        else:
            return 'link', uri, uri

