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
import view

from language import LANG as lang
from utils import menu_escape

from constants import RETWEET_NEW, RETWEET_OLD, UNSET_TEXT, MODE_TWEETS, \
                      HTML_UNSET_ID


class HTML(view.HTMLView):
    def __init__(self, main, gui):
        self.main = main
        self.gui = gui
        view.HTMLView.__init__(self, main, gui,
                               self.gui.html_scroll, MODE_TWEETS)
        
        self.item_count = self.main.load_tweet_count
        
        self.lang_loading = lang.html_loading
        self.lang_empty = lang.html_empty
        self.lang_load = lang.html_load_more
        
        self.last_name = UNSET_TEXT
        self.last_highlight = UNSET_TEXT
        self.last_mentioned = UNSET_TEXT
    
    
    # Items --------------------------------------------------------------------
    def get_latest(self):
        if self.main.settings.isset('lasttweet_' + self.main.username):
            return self.main.settings['lasttweet_' + self.main.username]
        
        else:
            return HTML_UNSET_ID
    
    def get_first(self):
        if self.main.settings.isset('firsttweet_' + self.main.username):
            return self.main.settings['firsttweet_' + self.main.username]
        
        else:
            return HTML_UNSET_ID
    
    def set_first(self, item_id):
        self.main.settings['firsttweet_' + self.main.username] = item_id
    
    def save_last_id(self, item_id=None):
        setting = 'lasttweet_' + self.main.username
        self.save_last(setting, item_id)
    
    def set_item_count(self, count):
        self.main.max_tweet_count = count
    
    def get_item_count(self):
        return self.main.max_tweet_count
    
    
    # Render the Timeline ------------------------------------------------------
    # --------------------------------------------------------------------------
    def render_item(self, num, item, img):
        # Check for new style retweet
        retweeted = False
        retweet = ''
        if hasattr(item, 'retweeted_status'):
            tweet = item.retweeted_status
            retweeted = True
            
            # Retweet Info
            retweet = '<a href="user:http://twitter.com/%s" title="''' \
                      + (self.relative_time(item.created_at)) + '">' \
                      + lang.html_in_retweet + '</a>'
            
            retweet = retweet % (item.user.screen_name,
                                    item.user.screen_name)
        
        else:
            tweet = item
        
        # Get User and Text
        user, formatted = tweet.user, self.parser.parse(tweet.text)
        
        
        # Spacers --------------------------------------------------------------
        highlight = self.main.username.lower() in \
                    [i.lower() for i in formatted.users]
        
        mentioned = hasattr(tweet, 'is_mentioned') and tweet.is_mentioned
        if num > 0:
            self.renderitems.insert(0,
                        self.insert_spacer(item, user, highlight, mentioned))
        
        self.last_name = user.screen_name
        self.last_highlight = highlight
        self.last_mentioned = mentioned
        
        # Is this tweet a reply?
        if tweet.in_reply_to_screen_name and tweet.in_reply_to_status_id:
            reply = ('<a href="status:http://twitter.com/%s/statuses/%d">' + \
                     lang.html_in_reply + '</a>') \
                     % (tweet.in_reply_to_screen_name,
                        tweet.in_reply_to_status_id,
                        tweet.in_reply_to_screen_name)
        
        else:
            reply = ''
        
        
        # Avatar ---------------------------------------------------------------
        self.is_new_avatar(num)
        if (num < len(self.items) - 1 \
           and (user.screen_name != self.get_screen_name(num + 1) \
           or self.new_avatar)  ) or num == len(self.items) - 1 \
           or self.new_timeline:
            
            avatar = self.avatar_html(user, num, img)
        
        else:
            avatar = ''
        
        
        # Background -----------------------------------------------------------
        if mentioned:
            clas = 'mentionedold' if item.id <= self.new_items_id \
                   else 'mentioned'
        
        elif item.id <= self.new_items_id:
            clas = 'highlightold' if highlight else 'oldtweet'
        
        else:
            clas = 'highlight' if highlight else 'tweet'
        
        
        # Source ---------------------------------------------------------------
        if tweet.source != 'web':
            if hasattr(tweet, 'source_url') and tweet.source_url != '':
                if tweet.source_url == '/devices':
                    tweet.source_url = 'http://twitter.com/devices'
                
                by_user = lang.html_by \
                          % ('<a href="source:%s" title="%s">%s</a>' \
                          % (tweet.source_url, tweet.source_url, tweet.source))
            
            else:
                by_user =  lang.html_by % tweet.source
        
        else:
            by_user = ''
        
        
        # Favorite -------------------------------------------------------------
        if tweet.favorited:
            favorite = '''<div class="undofav">
                          <a href="unfav:%s:%d" title="''' + \
                          lang.html_unfavorite + '''"> </a></div>'''
        
        else:
            favorite = '''<div class="dofav"><a href="fav:%s:%d" title="''' + \
                          lang.html_favorite + '''"> </a></div>'''
        
        
        # HTML Snippet ---------------------------------------------------------
        html = '''
        <div class="viewitem %s" id="%d"><div class="avatar">%s</div>
        <div class="actions">
            <div class="blocker"></div>
            <div class="doreply">
                <a href="qreply:%s:%d:%d" title="''' + \
                (lang.html_reply % user.screen_name) + \
                '''"> </a></div>''' + favorite + '''
        </div>
        <div class="inner-text">
            <div><span class="name">''' + \
                ('<b>RT</b> ' if retweeted else '') + \
                '''<b><a href="profile:http://twitter.com/%s" title="''' + \
                lang.html_profile + '''">%s</a></b></span>''' + \
                self.is_protected(user) + '''%s</div>
            <div class="time">
            <a href="status:http://twitter.com/%s/statuses/%d" title="''' + \
                self.absolute_time(tweet.created_at) + '''">%s</a>
                ''' + by_user + '''</div>
            <div class="reply">%s</div>
            <div class="reply">%s</div>
        </div>
        <div class="clearfloat"></div>
        </div>'''
        
        
        # Insert values
        html = html % (
                clas,
                num,
                avatar,
                
                # Actions
                user.screen_name, tweet.id, num,
                user.screen_name, tweet.id,
                
                # Text
                user.screen_name,
                user.name.strip(),
                user.screen_name,
                formatted.html,
                
                # Time
                user.screen_name,
                tweet.id,
                self.relative_time(tweet.created_at),
                reply, retweet)
        
        # Return the HTML string
        return html
        
        
    # Create Popup Items -------------------------------------------------------
    # --------------------------------------------------------------------------
    def ok_menu(self, link):
        return not link in ('fav', 'unfav', 'qreply')
    
    def create_menu(self, menu, item, item_id, link, full, user):
        # User Options
        if user is not None:
            if link in ('profile', 'avatar'):
                reply = 'reply:%s:%d:-1' % (user, item_id)
                self.add_menu_link(menu, lang.context_reply % menu_escape(user),
                                   self.context_link, reply, item)
            
            else:
                reply = 'reply:%s:-1:-1' % user
                self.add_menu_link(menu, lang.context_tweet % menu_escape(user),
                                   self.context_link, reply)
                        
            self.add_menu_separator(menu)
            message = 'message:%s:-1:-1' % user
            self.add_menu_link(menu, lang.context_message % menu_escape(user),
                               self.context_link, message)
        
            # Block / Unfollow
            if link == 'avatar':
                pass # TODO add this, but this needs additional api calls
        
        # Source
        elif link == 'source':
            source = self.get_source(item)
            self.add_menu_link(menu,
                               lang.context_source \
                               % lang.name(menu_escape(source)),
                               self.context_link, full)
        
        # More
        else:
            # Copy Tweet
            self.add_menu_link(menu, lang.context_copy_tweet,
                               self.copy_tweet, None, item)
            
            self.add_menu_separator(menu)
            
            # RT old
            name = self.get_screen_name(item)
            full = 'retweet:%s' % RETWEET_OLD
            self.add_menu_link(menu,
                               lang.context_retweet_old % menu_escape(name),
                               self.context_link, full, item)
            
            # RT New
            if name.lower() != self.main.username.lower() \
               and not self.get_protected(item):
                
                full = 'retweet:%s' % RETWEET_NEW
                self.add_menu_link(menu,
                                   lang.context_retweet_new % menu_escape(name),
                                   self.context_link, full, item)
            
            # Edit / Delete
            if name.lower() == self.main.username.lower():
                self.add_menu_separator(menu)
                full = 'edit:%d' % item_id
                self.add_menu_link(menu, lang.context_edit_tweet,
                                   self.context_link, full, item)
                
                full = 'delete:t:%d' % item_id
                self.add_menu_link(menu, lang.context_delete_tweet,
                                   self.context_link, full, item)
        
        return True

