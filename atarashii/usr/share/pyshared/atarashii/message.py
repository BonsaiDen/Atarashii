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

from language import LANG as lang

from constants import UNSET_TEXT, MODE_MESSAGES


class HTML(view.HTMLView):
    def __init__(self, main, gui):
        self.main = main
        self.gui = gui
        view.HTMLView.__init__(self, main, gui, 
                              self.gui.message_scroll, MODE_MESSAGES)
        
        self.get_latest = self.main.get_latest_message_id
        self.item_count = self.main.load_message_count
        
        self.get_item_count = self.main.get_message_count
        self.set_item_count = self.main.set_message_count
        
        self.lang_loading = lang.message_loading
        self.lang_empty = lang.message_empty
        self.lang_load = lang.message_load_more
        
        self.last_name = UNSET_TEXT
        self.last_recipient = UNSET_TEXT
        self.last_mentioned = UNSET_TEXT
        
        self.first_setting = 'firstmessage_'
    
    
    # Render the Timeline ------------------------------------------------------
    # --------------------------------------------------------------------------
    def render_item(self, num, item, img):
        user, text = item.sender, self.formatter.parse(item.text)
        
        
        # Spacers --------------------------------------------------------------
        mentioned = item.recipient_screen_name != self.main.username
        if num > 0:
            next_highlight = self.items[num + 1][0].recipient_screen_name != \
                self.main.username if num < len(self.items) - 1 else False
            
            force = self.last_recipient != item.recipient_screen_name
            self.renderitems.insert(0,
                        self.insert_spacer(item, user, False, mentioned,
                        next_highlight, force = force))
        
        self.last_mentioned = mentioned
        self.last_name = user.screen_name
        self.last_recipient = item.recipient_screen_name
        
        
        # Avatar ---------------------------------------------------------------
        self.is_new_avatar(num)
        if (num < len(self.items) - 1 and \
           (user.screen_name != self.items[num + 1][0].sender.screen_name \
           or item.recipient_screen_name != \
           self.items[num + 1][0].recipient_screen_name or self.new_avatar) \
           ) or num == len(self.items) - 1 or self.new_timeline:
            
            avatar = self.avatar_html(user, img)
        
        else:
            avatar = ""
        
        
        # Background -----------------------------------------------------------
        cls = 'oldtweet' if item.id <= self.init_id else 'tweet'
        if item.recipient_screen_name.lower() != self.main.username.lower():
            mode = lang.message_to
            name = item.recipient_screen_name
            reply = "display: none;"
            cls = "mentionedold" if item.id <= self.init_id else "mentioned"
            username = item.recipient_screen_name
            user_realname = item.recipient.name.strip()
            toid = item.recipient.id
            ltype = "rprofile"
        
        else:
            mode = lang.message_from
            name = user.screen_name
            reply = ""
            toid = user.id
            username = user.screen_name
            user_realname = user.name.strip()
            ltype = "profile"
        
                
        # HTML Snippet ---------------------------------------------------------
        html = '''
        <div class="viewitem %s" id="%d"><div class="avatar">%s</div>
        <div class="actions">
            <div class="doretweet" style="''' + reply + \
            '''"><a href="qmessage:%s:%d:%d" title="''' + \
                (lang.html_reply % user.screen_name) + '''"></a>
            </div>
        </div>
        
        <div class="inner-text">
            <div>
                <span class="name"><b>''' + mode + \
                ''' <a href="''' + ltype + \
                ''':http://twitter.com/%s" title="''' + \
                lang.html_profile + \
                '''">%s</a></b></span>''' + self.is_protected(user) + \
                '''%s</div>
            <div class="time">
            <a href="status:http://twitter.com/%s/statuses/%d" title="''' + \
                (self.absolute_time(item.created_at)) + '''">%s</a>
            </div>
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
                username,
                user_realname,
                name,
                text,
                
                # Time
                user.screen_name,
                item.id,
                self.relative_time(item.created_at))
        
        # Return the HTML string
        return html
    
    
    # Create Popup Items -------------------------------------------------------
    # --------------------------------------------------------------------------
    def ok_menu(self, link):
        return not link in ("qmessage",)
    
    def create_menu(self, menu, item, item_id, link, full, user):
        # User Options
        if user != None:
            if link == "profile" and user.lower() != self.main.username.lower():
                reply = "message:%s:%d:-1" % (user, self.get_recipient(item).id)
                self.add_menu_link(menu, lang.context_reply % user,
                                   lambda *args: self.context_link(reply,
                                                              extra = item))
            
            elif link == "rprofile" and \
               user.lower() != self.main.username.lower():
                reply = "message:%s:%d:-1" % (user, self.get_recipient(item).id)
                self.add_menu_link(menu, lang.context_message % user,
                                   lambda *args: self.context_link(reply,
                                                              extra = item))
            
            elif link == "user":
                reply = "message:%s:-1:-1" % user
                self.add_menu_link(menu, lang.context_message % user,
                                   lambda *args: self.context_link(reply))    
        
        # Retweet / Delete
        else:
            name = item.sender.screen_name
            if name.lower() == self.main.username.lower():
                full3 = "delete:m:%d" % item_id
                self.add_menu_link(menu, lang.context_delete_message,
                                   lambda *args: self.context_link(full3,
                                                               extra = item))
        
        return True

