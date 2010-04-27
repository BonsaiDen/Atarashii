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


# HTML View --------------------------------------------------------------------
# ------------------------------------------------------------------------------
import html

from utils import escape
from language import LANG as lang

from constants import ST_LOGIN_SUCCESSFUL
from constants import UNSET_TEXT, HTML_UNSET_TEXT, HTML_LOADED


class HTML(html.HTML):
    def __init__(self, main, gui):
        html.HTML.__init__(self, main, gui, True)
        self.item_count = self.main.load_tweet_count
        
        self.lang_loading = lang.profile_html_loading
        self.lang_empty = lang.profile_html_empty
        self.lang_load = lang.profile_html_load_more
        
        self.last_name = UNSET_TEXT
        self.last_highlight = UNSET_TEXT
        self.last_mentioned = UNSET_TEXT
        
        self.load_state = HTML_LOADED
    
    def render(self, user=None, friend=None, tweets=None):
        # If item don't have changed just update the times via javascript
        if not user:
            self.update_times()
            self.gui.update_app(True)
            return False
        
        # Add recent Tweets
        self.items = []
        for i in tweets:
            img_file = self.main.updater.get_image(i)
            self.update_list.append([i, img_file])
        
        while len(self.update_list) > 0:
            self.add(self.update_list.pop(0))
        
        # Init Render
        self.setup_render()
        self.init_id = 10000000000000
        self.new_items_id = self.init_id
        self.last_name = HTML_UNSET_TEXT
        self.last_highlight = False
        self.last_mentioned = False
        
        # Reset the user object associated with the avatar tooltip
        self.tooltip_user = None
        
        # Do the rendering!
        self.renderitems = []
        for num, obj in enumerate(self.items):
            item, img = obj
            self.is_new_timeline(item)
            self.renderitems.insert(0, self.render_item(num, item, img))
        
        # Image / Name / Tweets
        img_file = self.main.updater.get_image(None, False, user)
        
        # Detailed information
        details = []
        if user.url is not None and user.url.strip() != '':
            details.append(lang.profile_website % (escape(user.url),
                                                   escape(user.url)))
        
        if user.location is not None and user.location.strip() != '':
            details.append(lang.profile_location % escape(user.location))
        
        if user.description is not None and user.description.strip() != '':
            details.append(lang.profile_description % escape(user.description))
        
        # Status
        if friend[0].following and friend[0].followed_by:
            status = lang.profile_status_both
        
        elif friend[0].following:
            status = lang.profile_status_following
        
        elif friend[0].followed_by:
            status = lang.profile_status_followed
        
        elif friend[0].blocking:
            status = lang.profile_status_blocked
        
        elif user.protected:
            status = lang.profile_status_protected
        
        else:
            status = None
        
        if status is not None:
            status = '<div class="profile_status">%s</div>' % status
        
        else:
            status = HTML_UNSET_TEXT
        
        # Profile HTML
        self.profile_data = '''
        <div class="profile_header" id="header">
            <a href="user:%s:http://twitter.com/%s">
                <img class="profile_image" width="64" src="file://%s" />
            </a>
            <div class="profile_infos">   
                <div class="profile_realname">
                    <a href="user:%s:http://twitter.com/%s">%s</a>
                </div>
                <div><b>%s</b> Tweets</div>
                <div><b>%s</b> Followers</div>
                <div>Following <b>%s</b></div>
            </div>
            <div>
                <div>%s</div>
                %s
            </div>
        </div>''' % (user.screen_name, user.screen_name, img_file,
                     user.screen_name, user.screen_name, user.name,
                     user.statuses_count, user.followers_count,
                     user.friends_count, '</div><div>'.join(details), status)
        
        # Render
        self.set_html(self.renderitems, True)
    
    def after_loaded(self):
        self.execute_script(
            '''function resize() {
                   var header = document.getElementById('tweets');
                   if (header !== null) {
                       header.setAttribute('style', 'margin-top:' + 
                       (document.getElementById('header').offsetHeight) + 'px');
                   }
                   delete header;
                };window.onresize = resize;resize();''')
    
    def set_html(self, renderitems, rendered=False):
        if rendered:
            if len(self.items) > 0:
                self.render_html('''
                    <body ondragstart="return false">
                        %s
                        <div id="tweets">
                            <div id="newcontainer"></div>
                            <div>%s</div>
                        </div>
                    </body>''' % (self.profile_data, ''.join(renderitems)))
            
            else:
                self.render_html('''
                    <body class="unloaded" ondragstart="return false">
                        %s
                        <div id="tweets" class="profile_tweets">
                            <div class="loading">
                                <b>%s</b>
                            </div>
                        </div>
                    </body>''' % (self.profile_data, self.lang_empty))
        
        elif self.main.status(ST_LOGIN_SUCCESSFUL):
            self.render_html('''
                <body class="unloaded" ondragstart="return false">
                    <div class="loading" style="padding-top: 6px">
                        <b>%s</b>
                    </div>
                </body>''' % self.lang_empty)

