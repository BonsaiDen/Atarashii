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

from lang import lang

from constants import RETWEET_NEW, RETWEET_OLD


class HTML(view.HTMLView):
    def __init__(self, main, gui):
        self.main = main
        self.gui = gui
        view.HTMLView.__init__(self, main, gui, self.gui.html_scroll)
        self.get_latest = self.main.get_latest_id
        self.item_count = self.main.load_tweet_count
        
        self.get_item_count = self.main.get_tweet_count
        self.set_item_count = self.main.set_tweet_count
        
        self.lang_loading = lang.html_loading
        self.lang_empty = lang.html_empty
        self.lang_load = lang.html_load_more
        
        self.first_setting = 'firsttweet_'
    
    
    # Render the Timeline ------------------------------------------------------
    # --------------------------------------------------------------------------
    def render_item(self, num, item, img):
        # Check for new style retweet
        retweeted = False
        retweet = ""
        if hasattr(item, "retweeted_status"):
            tweet = item.retweeted_status
            retweeted = True
            
            # Retweet Info
            retweet = '<a href="user:http://twitter.com/%s" title="''' + \
                    (self.relative_time(item.created_at)) + '">' + \
                    lang.html_in_retweet + '</a>'
            retweet = retweet % (item.user.screen_name,
                                    item.user.screen_name)
        
        else:
            tweet = item
        
        # Get User and Text
        user, text = tweet.user, self.formatter.parse(tweet.text)
        
        
        # Spacers ----------------------------------------------------------
        highlight = self.main.username.lower() in \
                        [i.lower() for i in self.formatter.users]
        mentioned = hasattr(tweet, "is_mentioned") and tweet.is_mentioned
        if num > 0:
            self.renderitems.insert(0,
                        self.insert_spacer(item, user, highlight, mentioned))
        
        self.lastname = user.screen_name
        self.last_highlight = highlight
        self.last_mentioned = mentioned
        
        # Is this tweet a reply?
        if tweet.in_reply_to_screen_name and tweet.in_reply_to_status_id:
            reply = '<a href="status:http://twitter.com/%s/statuses/%d">' + \
                    lang.html_in_reply + '</a>'
            reply = reply % (tweet.in_reply_to_screen_name,
                            tweet.in_reply_to_status_id,
                            tweet.in_reply_to_screen_name)
        else:
            reply = ""
        
        
        # Avatar -----------------------------------------------------------
        self.is_new_avatar(num)
        if (num < len(self.items) - 1 and \
            (user.screen_name != self.get_user(num + 1).screen_name or \
            self.new_avatar) \
            ) or num == len(self.items) - 1 or self.new_timeline:
            
            avatar = '''<a href="profile:http://twitter.com/%s">
                        <img width="32" src="file://%s" title="''' + \
                        lang.html_info + '''"/></a>'''
            
            avatar = avatar % (user.screen_name, img,
                                user.name, user.followers_count,
                                user.friends_count,
                                user.statuses_count)
        
        else:
            avatar = ""
        
        
        # Background -------------------------------------------------------
        if mentioned:
            clas = "mentionedold" if item.id <= self.init_id else "mentioned"
        
        elif item.id <= self.init_id:
            clas = 'highlightold' if highlight else 'oldtweet'
        
        else:
            clas = 'highlight' if highlight else 'tweet'
        
        
        # Source -----------------------------------------------------------
        if tweet.source != "web":
            if hasattr(tweet, "source_url") and tweet.source_url != "":
                by_user = lang.html_by % ('<a href="source:%s" title="%s">%s</a>' % \
                        (tweet.source_url, tweet.source_url, tweet.source))
            
            else:
                by_user =  lang.html_by % tweet.source
        
        else:
            by_user = ""
        
        
        # Protected --------------------------------------------------------
        if hasattr(user, "protected") and user.protected:
            locked = ('<span class="protected" title="' + \
                lang.html_protected + '"></span>') % user.screen_name
        
        else:
            locked = ''
        
        
        # HTML Snippet -----------------------------------------------------
        html = '''
        <div class="viewitem %s" id="%d">
        <div class="avatar">
            %s
        </div>
        
        <div class="actions">
            <div class="doreply">
                <a href="reply:%s:%d:%d" title="''' + \
                (lang.html_reply % user.screen_name) + '''"> </a>
            </div>
        </div>
        
        <div class="inner-text">
            <div><span class="name">''' + \
                ("<b>RT</b>" if retweeted else "") + '''
                 <b><a href="profile:http://twitter.com/%s" title="''' + \
                lang.html_profile + '''">
                   %s
                </a></b></span> ''' + locked + ''' %s
            </div>
            <div class="time">
                <a href="status:http://twitter.com/%s/statuses/%d" title="''' + \
                (self.absolute_time(tweet.created_at)) + '''">%s</a>
                ''' + by_user + '''
            </div>
            <div class="reply">%s</div>
            <div class="reply">%s</div>
        </div>
        <div class="clearfloat"></div>
        </div>'''
        
        #             <div class="doretweet">
        #        <a href="retweet:%d:%d:-1" title="''' + \
        #        (lang.html_retweet % user.screen_name) + '''"> </a>
        #    </div>
        
        # Insert values
        html = html % (
                clas,
                num,
                avatar,
                
                # Actions
                user.screen_name, tweet.id, num,
                #num, tweet.id,
                
                # Text
                user.screen_name,
                user.name.strip(),
                user.screen_name,
                text,
                
                # Time
                user.screen_name,
                tweet.id,
                self.relative_time(tweet.created_at),
                reply, retweet)
        
        # Return the HTML string
        return html
        
        
    # Create Popup Items -------------------------------------------------------
    # --------------------------------------------------------------------------
    def create_menu(self, menu, item):
        link, url, full = self.get_link_type(self.clicked_link)
        
        # Get the real ID
        if item != None:
            item_id = self.get_id(item)
        
        # Link options
        if link == "link":
            self.add_menu_link(menu, "Open in Browser",
                               lambda *args: self.context_link(full))
            
            self.add_menu_link(menu, "Copy",
                               lambda *args: self.copy_link(full))  
                
        # User Options
        elif link == "user" or link == "profile":
            user = full[full.rfind("/") + 1:]
            self.add_menu_link(menu, "Visit %s's Profile" % user,
                               lambda *args: self.context_link(full))
            
            if link == "profile":
                reply = "reply:%s:%d:-1" % (user, item_id)
                self.add_menu_link(menu, "Reply to %s" % user,
                                   lambda *args: self.context_link(reply, 
                                                              extra = item))
            
            else:
                reply = "reply:%s:-1:-1" % user
                self.add_menu_link(menu, "Tweet to %s" % user,
                                   lambda *args: self.context_link(reply))    
        
        # Source
        elif link == "source":
            by = self.get_source(item)
            self.add_menu_link(menu, "%s's Homepage" % by,
                               lambda *args: self.context_link(full))
        
        # Status
        elif link == "status":
            self.add_menu_link(menu, "View on Twitter.com",
                               lambda *args: self.context_link(full))   
        
        # Tag
        elif link == "tag":
            self.add_menu_link(menu, "Search on Twitter.com",
                               lambda *args: self.context_link(full))   
        
        # Retweet / Delete
        else:
            name = self.get_user(item).screen_name
            full1 = "retweet:%s" % RETWEET_OLD
            self.add_menu_link(menu, "Retweet %s via RT" % name,
                               lambda *args: self.context_link(full1,
                                                           extra = item))
            
            if name.lower() != self.main.username.lower():
                full2 = "retweet:%s" % RETWEET_NEW
                self.add_menu_link(menu, "Retweet %s via Twitter" % name,
                                   lambda *args: self.context_link(full2,
                                                               extra = item))
            
            if name.lower() == self.main.username.lower():
                self.add_menu_separator(menu)
                full3 = "delete:t:%d" % item_id
                mitem = self.add_menu_link(menu, "Delete this Tweet",
                                   lambda *args: self.context_link(full3,
                                                               extra = item))
                
                mitem.set_sensitive(False)
        
