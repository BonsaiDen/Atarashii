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


# HTML View / HTML -------------------------------------------------------------
# ------------------------------------------------------------------------------
from constants import SPACES

from language import LANG as lang
from constants import HTML_UNSET_ID, HTML_UNSET_TEXT, UNSET_USERNAME
from constants import ST_NETWORK_FAILED, ST_LOGIN_SUCCESSFUL


class ViewHTML(object):
    def init_render(self):
        self.position = self.scroll.get_vscrollbar().get_value()
        self.current_scroll = self.position
        self.is_loading = True
        self.items.sort(key = lambda i: i[0].id)
        self.count = 0
        
        # Newest Stuff
        self.newest = False
        self.newest_avatar = False
        self.new_timeline = False
        self.new_items_id = HTML_UNSET_ID
        if self.newest_id == HTML_UNSET_ID:
            self.newest_id = self.init_id
        
        # Find newest item
        for item in self.items:
            name = self.get_screen_name(item[0], True).lower()
            if item[0].id > self.init_id and name != self.main.username.lower():
                self.new_items_id = item[0].id - 1
                break
        
        if self.new_items_id == HTML_UNSET_ID:
            if len(self.items) > 0:
                self.new_items_id = self.items[len(self.items) - 1][0].id
            
            else:
                self.new_items_id = self.init_id
    
    def render(self, update_multi=False):
        self.init_render()
        self.last_name = HTML_UNSET_TEXT
        self.last_recipient = HTML_UNSET_TEXT
        self.last_highlight = False
        self.last_mentioned = False
        
        # Reset the user object associated to the avatar tooltip
        self.tooltip_user = None
        
        # Do the rendering!
        self.renderitems = []
        newest_closed = False
        for num, obj in enumerate(self.items):
            item, img = obj
            self.is_new_timeline(item)
            self.renderitems.insert(0, self.render_item(num, item, img))
            
            # Close new container
            # This thing is what calculates the scrolling offset when new tweets
            # come in in order to make the view stay at the exact same tweet
            # is was before
            # coung gets increased in render_item!
            if self.first_load:
                if self.count > 0 and not newest_closed:
                    newest_closed = True
                    self.renderitems.insert(2, '</div>')
            
            else:
                if item.id >= self.newest_id and not newest_closed:
                    newest_closed = True
                    self.renderitems.insert(0, '</div>')
        
        # make sure to close the new container
        if not newest_closed:
            self.renderitems.insert(0, '</div>')
        
        # Render
        self.set_html(self.renderitems, True)
        
        # Update multi button
        if update_multi:
            self.gui.set_multi_button(not self.main.status(ST_NETWORK_FAILED))
    
    
    # HTML Helpers -------------------------------------------------------------
    def update_css(self):
        try:
            self.execute_script('''
                 document.getElementsByTagName('link')[0].href='%s'
                 ''' % self.main.settings.css_file)
        
        except Exception:
            pass
    
    def start(self):
        self.scroll.get_vscrollbar().set_value(0)
        self.offset_count = 0
        self.render_html('''
            <body class="unloaded" ondragstart="return false">
                <div class="loading"><img src="file://%s" /><br/>
                <b class="loadingtext">%s</b></div>
            </body>''' % (self.main.get_image(), self.lang_loading))
    
    def splash(self):
        self.scroll.get_vscrollbar().set_value(0)
        self.offset_count = 0
        acc = lang.html_account if self.main.username == UNSET_USERNAME \
                                else HTML_UNSET_TEXT
        
        acc_info = lang.html_account_info \
                   if self.main.username == UNSET_USERNAME else HTML_UNSET_TEXT
        
        self.render_html('''
            <body class="unloaded" ondragstart="return false">
                <div class="loading">
                <img src="file://%s" /><br/>
                <b class="loadingtext">%s</b>
                <div class="infoheader">%s</div>
                <div class="infotext">%s</div>
                </div>
            </body>''' % (self.main.get_image(), lang.html_welcome, acc,
                          acc_info))
    
    def render_html(self, html):
        data = '''
        <html>
        <head>
        <meta content="text/html; charset=UTF-8" http-equiv="content-type"/>
        <link rel="stylesheet" type="text/css" media="screen" href="file://%s"/>
        </head>
        %s
        </html>''' % (self.main.settings.css_file, html)
        
        # FIXME This memory leaks EXTREMLY hard!
        # Even removing the dom stuff per javascript doesn't help
        # I guess it's a problem with the html data not beeing freed somewhere
        # in the python c bindings
        if self.load_history:
            self.is_rendering_history = True
        
        self.load_string(SPACES.sub(' ', data),
                         'text/html', 'UTF-8', 'file:///')
    
    def set_html(self, renderitems, rendered=False):
        self.gui.set_app_title()
        if rendered:
            if len(self.items) > 0:
                self.render_html('''
                    <body ondragstart="return false">
                        <div><div id="newcontainer">%s</div>
                        <div class="loadmore">
                        <a href="more:%d"><b>%s</b></a>
                        </div>
                    </body>''' % (''.join(renderitems),
                                    self.items[0][0].id, self.lang_load))
            
            else:
                self.render_html('''
                    <body class="unloaded" ondragstart="return false">
                        <div class="loading"><b>%s</b></div>
                    </body>''' % self.lang_empty)
        
        elif self.main.status(ST_LOGIN_SUCCESSFUL):
            self.render_html('''
                <body class="unloaded" ondragstart="return false">
                    <div class="loading"><b>%s</b></div>
                </body>''' % self.lang_empty)
    
    # The big magic spacer inserted... trust me it's really magic that this
    # thin does work at all...
    def insert_spacer(self, item, user, highlight, mentioned,
                      next_highlight=False, force=False, message=False):
        
        spacer = 'foo'
        if item.id > self.new_items_id:
            
            # Name change
            if self.last_name != user.screen_name or self.new_timeline or force:
                if message and (mentioned or self.last_mentioned):
                    if not self.last_mentioned or not mentioned:
                        spacer = 'tweet_highlight'
                    
                    else:
                        spacer = 'message' if message \
                                               else 'spacer_mention'
                
                elif (mentioned or self.last_mentioned) and not highlight:
                    if not self.last_mentioned:
                        spacer = 'spacer_message_new' if message \
                                                      else 'spacer_mention_new'
                    
                    else:
                        spacer = 'message' if message else 'spacer_mention'
                
                elif highlight and self.last_highlight:
                    spacer = 'highlight'
                
                elif highlight or self.last_highlight:
                    spacer = 'tweet_highlight'
                
                else:
                    spacer = 'tweet'
            
            else:
                
                # More mentions
                if mentioned:
                    if not self.last_mentioned:
                        spacer = 'tweet' if message else 'mention'
                    
                    else:
                        spacer = 'message' if message else 'mention'
                
                # More @username
                elif highlight:
                    if not self.last_highlight:
                        spacer = 'tweet_highlight'
                    
                    else:
                        spacer = 'in_highlight'
                
                # Just more normal tweets
                else:
                    if next_highlight and self.last_highlight:
                        spacer = 'tweet'
                    
                    elif next and self.last_mentioned:
                        spacer = 'tweet'
                    
                    elif self.last_highlight:
                        spacer = 'tweet_highlight'
                    
                    else:
                        spacer = 'in_tweet'
        
        # Old Tweets
        else:
            
            # Name change
            if self.last_name != user.screen_name or self.new_timeline or force:
                if message and (mentioned or self.last_mentioned):
                    if not self.last_mentioned or not mentioned:
                        spacer = 'tweet_highlight_old'
                    
                    else:
                        spacer = 'message_old' if message \
                                               else 'spacer_mention_old'
                
                elif (mentioned or self.last_mentioned) and not highlight:
                    spacer = 'message_old' if message \
                                           else 'spacer_mention_old'
                
                elif highlight and self.last_highlight:
                    spacer = 'highlight_old'
                
                elif highlight or self.last_highlight:
                    spacer = 'tweet_highlight_old'
                
                else:
                    spacer = 'tweet_old'
            
            else:
                
                # More mentions
                if mentioned:
                    if not self.last_mentioned:
                        spacer = 'tweet_old' if message else 'mention_old'
                    
                    else:
                        spacer = 'message_old' if message else 'mention_old'
                
                # More @username
                elif highlight:
                    if not self.last_highlight:
                        spacer = 'tweet_highlight_old'
                    
                    else:
                        spacer = 'in_highlight_old'
                
                # Just more normal tweets
                else:
                    if next_highlight and self.last_highlight:
                        spacer = 'tweet_old'
                    
                    elif next and self.last_mentioned:
                        spacer = 'tweet'
                    
                    elif self.last_highlight:
                        spacer = 'tweet_highlight_old'
                    
                    else:
                        spacer = 'in_tweet_old'
        
        return '<div class="spacer_%s"></div>' % spacer
    
    def avatar_html(self, user, num, img):
        return '''<a href="avatar:%d:http://twitter.com/%s">
                  <img class="avatarimage" src="file://%s" title="avatar"/>
                  </a>''' % (num, user.screen_name, img)

