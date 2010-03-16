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

from lang import lang


class HTML(view.HTMLView):
    def __init__(self, main, gui):
        self.main = main
        self.gui = gui
        view.HTMLView.__init__(self, main, gui, self.gui.message_scroll)
        self.get_latest = self.main.get_latest_message_id
        self.item_count = self.main.load_message_count
        
        self.get_item_count = self.main.get_message_count
        self.set_item_count = self.main.set_message_count
        
        self.lang_loading = lang.message_loading
        self.lang_empty = lang.message_empty
        self.lang_load = lang.message_load_more
        
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
            
            force = self.lastrecipient != item.recipient_screen_name
            self.renderitems.insert(0,
                        self.insert_spacer(item, user, False, mentioned, True,
                        next_highlight, force = force))
        
        self.last_mentioned = mentioned
        self.lastname = user.screen_name
        self.lastrecipient = item.recipient_screen_name
        
        
        # Avatar ---------------------------------------------------------------
        self.is_new_avatar(num)
        if (num < len(self.items) - 1 and \
           (user.screen_name != self.items[num + 1][0].sender.screen_name \
           or item.recipient_screen_name != \
           self.items[num + 1][0].recipient_screen_name or self.new_avatar) \
           ) or num == len(self.items) - 1 or self.new_timeline:
            
            avatar = '''<a href="profile:http://twitter.com/%s">
                        <img width="32" src="file://%s" title="''' + \
                        lang.html_info + '''"/></a>'''
            
            avatar = avatar % (user.screen_name, img,
                                user.name,
                                user.followers_count,
                                user.friends_count,
                                user.statuses_count)
            
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
            ltype = "user"
        
        else:
            mode = lang.message_from
            name = user.screen_name
            reply = ""
            username = user.screen_name
            user_realname = user.name.strip()
            ltype = "profile"
        
                
        # HTML Snippet ---------------------------------------------------------
        html = '''
        <div class="viewitem %s" id="%d">
        <div class="avatar">
            %s
        </div>
        
        <div class="actions">
            <div class="doretweet" style="''' + reply + \
            '''"><a href="message:%s:%d:%d" title="''' + \
                (lang.html_reply % user.screen_name) + '''"></a>
            </div>
        </div>
        
        <div class="inner-text">
            <div>
                <span class="name"><b>''' + mode + \
                ''' <a href="''' + ltype + \
                ''':http://twitter.com/%s" title="''' + \
                lang.html_profile + \
                '''">%s</a></b></span>''' + self.is_protected(user) + '''%s</div>
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
                user.screen_name, user.id, num,
                
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
    def create_menu(self, menu, item, link):
        link, url, full = self.get_link_type(link)
        
        # Get the real ID
        if item != None:
            item_id = self.get_id(item)
        
        # Link options
        if link == "link":
            self.add_menu_link(menu, lang.context_browser,
                               lambda *args: self.context_link(full))
            
            self.add_menu_link(menu, lang.context_copy,
                               lambda *args: self.copy_link(full))  
        
        # User Options
        elif link == "user" or link == "profile":
            user = full[full.rfind("/") + 1:]
            self.add_menu_link(menu, lang.context_profile % user,
                               lambda *args: self.context_link(full))
            
            if link == "profile" and user.lower() != self.main.username.lower():
                reply = "message:%s:%d:-1" % (user, item_id)
                self.add_menu_link(menu, lang.context_reply % user,
                                   lambda *args: self.context_link(reply,
                                                              extra = item))
            
            elif link == "user":
                reply = "message:%s:-1:-1" % user
                self.add_menu_link(menu, lang.context_message % user,
                                   lambda *args: self.context_link(reply))    
        
        # Status
        elif link == "status":
            self.add_menu_link(menu, lang.context_view,
                               lambda *args: self.context_link(full))   
        
        # Tag
        elif link == "tag":
            self.add_menu_link(menu, lang.context_search,
                               lambda *args: self.context_link(full))   
        
        # Retweet / Delete
        else:
            name = item.sender.screen_name
            if name.lower() == self.main.username.lower():
                full3 = "delete:m:%d" % item_id
                self.add_menu_link(menu, lang.context_delete_message,
                                   lambda *args: self.context_link(full3,
                                                               extra = item))

