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
import view_tweet as tweet

from utils import escape
from lang import LANG as lang

from constants import UNSET_TEXT, HTML_UNSET_TEXT, UNSET_URL, UNSET_STRING
from constants import HTML_LOADED


class HTML(tweet.HTML):
    def __init__(self, main, gui):
        tweet.HTML.__init__(self, main, gui, True)
        self.item_count = self.main.load_tweet_count
        
        self.lang_loading = lang.profile_html_loading
        self.lang_empty = lang.profile_html_empty
        self.lang_load = lang.profile_html_load_more
        
        self.last_name = UNSET_TEXT
        self.last_highlight = UNSET_TEXT
        self.last_mentioned = UNSET_TEXT
        
        self.current_user = None
        self.protected_view = False
        self.load_state = HTML_LOADED
    
    def render(self, user=None, friend=None, tweets=None, force_render=False):
        # If item don't have changed just update the times via javascript
        if not user and not force_render:
            self.update_times()
            self.gui.update_app(True)
            return False
        
        # Add recent Tweets
        if not force_render:
            self.items = []
        
        if tweets is not None:
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
        
        # Render header
        if user is not None:
            self.render_header(user, friend)
        
        # Render
        self.set_html(self.renderitems, True)
    
    
    def render_header(self, user, friend):
        img_file = self.main.updater.get_image(None, False, user)
        
        # Detailed information
        details = []
        if user.url is not None and user.url.strip() != UNSET_URL:
            details.append(lang.profile_website % (escape(user.url),
                                                   escape(user.url)))
        
        if user.location is not None and user.location.strip() != UNSET_STRING:
            details.append(lang.profile_location % escape(user.location))
        
        if user.description is not None \
           and user.description.strip() != UNSET_STRING:
            
            details.append(lang.profile_description % escape(user.description))
        
        # Display the protected Info?
        if user.protected and not friend[0].following:
            self.protected_view = True
        
        else:
            self.protected_view = False
        
        # Profile HTML
        style = 'style="display:none;"' \
                if user.screen_name.lower() == self.main.username.lower() \
                else HTML_UNSET_TEXT
        
        self.profile_data = '''
        <div class="profile_header" id="header">
            <a href="http://twitter.com/%s">
                <img class="profile_image" width="64" src="file://%s" />
            </a>
            <div class="profile_infos">   
                <div class="profile_realname">
                    <a href="http://twitter.com/%s">%s</a>
                </div>
                <div><b>%s</b> %s%s</div>
                <div><b>%s</b> %s</div>
                <div>%s <b>%s</b>%s</div>
            </div>
            <div>
                <div>%s</div>
                <div ''' + style + '''>
                    <input id="follow_button" type="button" value="%s"
                     onclick="follow(%d, '%s', %d);"/>
                    <input id="block_button" type="button" value="%s"
                     onclick="block(%d, '%s', %d);"/>
                    <input id="message_button" type="button" value="%s"
                     onclick="message('%s', %d);"/>
                </div>
            </div>
            <script type="text/javascript">
                var follow_button = document.getElementById('follow_button');
                var block_button = document.getElementById('block_button');
                function follow(id, name, mode) {
                    enable_buttons(false);
                    window.location = ['follow', id, name, mode].join(':');
                }
                
                function block(id, name, mode) {
                    enable_buttons(false);
                    window.location = ['block', id, name, mode].join(':');
                }
                
                function message(name, id) {
                    window.location = ['message', name, id, -1].join(':');
                }
                
                function enable_buttons(mode) {
                    follow_button.disabled = !mode;
                    block_button.disabled = !mode;
                }
            </script>
        </div>'''
        
        self.current_user = user
        self.profile_data = self.profile_data % (
             user.screen_name, img_file, user.screen_name, escape(user.name),
             user.statuses_count, lang.profile_tweets,
             lang.profile_protected if user.protected \
                                    else HTML_UNSET_TEXT,
             
             user.followers_count, lang.profile_followers,
             lang.profile_following, user.friends_count,
             lang.profile_follows_you if friend[0].followed_by \
                                      else HTML_UNSET_TEXT,
             
             '</div><div>'.join(details),
             lang.profile_unfollow if friend[0].following \
                                   else lang.profile_follow,
             
             user.id, user.screen_name, int(not friend[0].following),
             
             lang.profile_unblock if friend[0].blocking \
                                  else lang.profile_block,
             
             user.id, user.screen_name, int(not friend[0].blocking),
             lang.profile_message, user.screen_name, user.id)
    
    
    # JavaScript stuff ---------------------------------------------------------
    def update_follow(self, mode):
        self.execute_script('''
            document.getElementById('follow_button').value = '%s';
            document.getElementById('follow_button').setAttribute('onclick',
            "follow(%d, '%s', %d);");
            enable_buttons(true);''' % (
            lang.profile_unfollow if mode else lang.profile_follow,
            self.current_user.id, self.current_user.screen_name, int(not mode)))
    
    def update_block(self, mode):
        self.execute_script('''
            document.getElementById('block_button').value = '%s';
            document.getElementById('block_button').setAttribute('onclick',
            "block(%d, '%s', %d);");
            enable_buttons(true);''' % (
            lang.profile_unblock if mode else lang.profile_block,
            self.current_user.id, self.current_user.screen_name, int(not mode)))
    
    def enable_button(self):
        self.execute_script('enable_buttons(true);')
    
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
    
    
    # Run some crazy javascript in order to calculate all the positioning
    def get_sizes(self, event):
        try:
            self.menu_javascript(
                 'var pos = document.getElementById(\'header\').offsetHeight;',
                 event)
            
            return self.get_main_frame().get_title()
        
        except Exception:
            return None
    
    def set_html(self, renderitems, rendered=False):
        if rendered:
            if len(self.items) > 0:
                self.render_html('''
                    <body ondragstart="return false">
                        %s
                        <div id="tweets">
                            <div id="newcontainer"></div>
                            <div>%s</div>
                            <div class="loadmore">
                                <a href="more:%d"><b>%s</b></a>
                            </div>
                        </div>
                    </body>''' % (self.profile_data,
                                  HTML_UNSET_TEXT.join(renderitems),
                                  self.items[0][0].id, self.lang_load))
            
            else:
                self.render_html('''
                    <body class="unloaded" ondragstart="return false">
                        %s
                        <div id="tweets" class="profile_tweets">
                            <div class="loading">
                                <div class="profile_empty"><b>%s</b></div>
                            </div>
                        </div>
                    </body>''' % (self.profile_data,
                                  lang.profile_html_protected \
                                  if self.protected_view else self.lang_empty))

