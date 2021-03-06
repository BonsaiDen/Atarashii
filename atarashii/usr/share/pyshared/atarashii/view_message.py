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


# HTML View --------------------------------------------------------------------
# ------------------------------------------------------------------------------
import view

from utils import menu_escape
from lang import LANG as lang

from constants import UNSET_TEXT, UNSET_ID_NUM, MODE_MESSAGES, HTML_UNSET_ID, \
                      HTML_UNSET_TEXT


class HTML(view.HTMLView):
    def __init__(self, main, gui):
        view.HTMLView.__init__(self, main, gui,
                               gui.message_scroll, MODE_MESSAGES)
        
        self.item_count = self.main.load_message_count
        
        self.lang_loading = lang.message_loading
        self.lang_empty = lang.message_empty
        self.lang_load = lang.message_load_more
        
        self.last_name = UNSET_TEXT
        self.last_recipient = UNSET_TEXT
        self.last_mentioned = UNSET_TEXT
    
    
    # Items --------------------------------------------------------------------
    def get_latest(self):
        if self.main.settings.isset('lastmessage_' + self.main.username):
            return self.main.settings['lastmessage_' + self.main.username]
        
        else:
            return HTML_UNSET_ID
    
    def get_first(self):
        if self.main.settings.isset('firstmessage_' + self.main.username):
            return self.main.settings['firstmessage_' + self.main.username]
        
        else:
            return HTML_UNSET_ID
    
    def set_first(self, item_id):
        self.main.settings['firstmessage_' + self.main.username] = item_id
    
    def save_last_id(self, item_id=None):
        setting = 'lastmessage_' + self.main.username
        self.save_last(setting, item_id)
    
    def set_item_count(self, count):
        self.main.max_message_count = count
    
    def get_item_count(self):
        return self.main.max_message_count
    
    
    # Render the Timeline ------------------------------------------------------
    # --------------------------------------------------------------------------
    def render_item(self, num, item, img):
        user, formatted = item.sender, self.parser.parse(item.text)
        
        
        # Spacers --------------------------------------------------------------
        mentioned = item.recipient_screen_name != self.main.username
        if num > 0:
            next_highlight = self.items[num + 1][0].recipient_screen_name \
                             != self.main.username if num < len(self.items) \
                             - 1 else False
            
            force = self.last_recipient != item.recipient_screen_name
            self.renderitems.insert(0,
                        self.insert_spacer(item, user, False, mentioned,
                        next_highlight, force = force, message = True))
        
        self.last_mentioned = mentioned
        self.last_name = user.screen_name
        self.last_recipient = item.recipient_screen_name
        
        
        # Avatar ---------------------------------------------------------------
        self.is_new_avatar(num)
        has_avatar = (num < len(self.items) - 1 and (user.screen_name != \
                     self.items[num + 1][0].sender.screen_name \
                     or self.new_avatar)) \
                     or num == len(self.items) - 1 or self.new_timeline
        
        avatar, text_class = self.get_avatar(has_avatar, user, num, img)
        
        
        # Background -----------------------------------------------------------
        cls = 'oldtweet' if item.id <= self.new_items_id else 'tweet'
        if item.recipient_screen_name.lower() != self.main.username.lower():
            mode = lang.message_to
            name = item.recipient_screen_name
            reply = 'display: none;'
            cls = 'messageold' if item.id <= self.new_items_id \
                   else 'message'
            
            username = item.recipient_screen_name
            toid = item.recipient.id
            ltype = 'rprofile'
        
        else:
            mode = lang.message_from
            name = user.screen_name
            reply = HTML_UNSET_TEXT
            toid = user.id
            username = user.screen_name
            ltype = 'profile'
        
        
        # HTML Snippet ---------------------------------------------------------
        html = '''
        <div class="viewitem %s" id="%d"><div class="avatar">%s</div>
        <div class="actions">
            <div class="doretweet" style="''' + reply \
                + '''"><a href="qmessage:%s:%d:%d" title="''' \
                + (lang.html_reply % user.screen_name) + '''"></a>
            </div>
        </div>
        
        <div class="''' + text_class + '''">
            <div>
                <span class="name"><b>''' + mode \
                + ''' <a href="''' + ltype \
                + ''':%d:http://twitter.com/%s" title="''' \
                + lang.html_profile \
                + '''">%s</a></b></span>''' \
                + self.is_protected(user) \
                + '''%s</div>
            <div id="time_%d" class="time" title="''' + \
            self.absolute_time(item.created_at, True) + '''">%s</div>
        </div>
        </div>'''
        
        # Insert values
        html = html % (
                cls,
                num,
                avatar,
                
                # Actions
                user.screen_name, toid, num,
                
                # Text
                num,
                username,
                lang.name(username),
                name,
                formatted.html.replace('\n', '<br/>'),
                
                # Time
                num,
                self.relative_time(item.created_at))
        
        # Return the HTML string
        return html
    
    
    # Create Popup Items -------------------------------------------------------
    # --------------------------------------------------------------------------
    def ok_menu(self, link):
        return not link in ('qmessage',)
    
    def create_menu(self, menu, item, item_id, link, full, user):
        # User Options
        if user is not None:
            if link in ('profile', 'avatar') \
               and user.lower() != self.main.username.lower():
                
                reply = 'message:%s:%d:%d' % (user, self.get_sender(item).id,
                                              HTML_UNSET_ID)
                
                self.add_menu_link(menu,
                                   lang.context_reply % menu_escape(user),
                                   self.context_link, reply, item)
            
            elif link == 'rprofile' \
                 and user.lower() != self.main.username.lower():
                
                reply = 'message:%s:%d:%d' % (user, self.get_recipient(item).id,
                                              HTML_UNSET_ID)
                
                self.add_menu_link(menu,
                                   lang.context_message % menu_escape(user),
                                   self.context_link, reply, item)
            
            elif link == 'user':
                reply = 'message:%s:%d:%d' % (user, UNSET_ID_NUM, HTML_UNSET_ID)
                self.add_menu_link(menu,
                                   lang.context_message % menu_escape(user),
                                   self.context_link, reply)
        
        else:
            
            # Copy Message
            self.add_menu_link(menu, lang.context_copy_message,
                               self.copy_message, None, item)
            
            # Delete
            name = item.sender.screen_name
            if name.lower() == self.main.username.lower():
                self.add_menu_separator(menu)
                full = 'delete:m:%d' % item_id
                self.add_menu_link(menu, lang.context_delete_message,
                                   self.context_link, full, item)

