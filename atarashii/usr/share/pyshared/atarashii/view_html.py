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
from utils import compare_sub

from language import LANG as lang
from constants import HTML_UNSET_ID, ST_LOGIN_SUCCESSFUL


class ViewHTML:
    def __init__(self):
        pass
    
    # Render the actual HTML ---------------------------------------------------
    # --------------------------------------------------------------------------
    def init_render(self):
        self.position = self.scroll.get_vscrollbar().get_value()
        self.items.sort(compare_sub)
        self.count = 0
        
        # Newest Stuff
        self.newest = False
        self.newest_avatar = False
        self.new_timline = False
        if self.newest_id == HTML_UNSET_ID:
            self.newest_id = self.init_id
    
    def render(self):
        self.init_render()
        self.last_name = ""
        self.last_recipient = ""
        self.last_highlight = False
        self.last_mentioned = False
        
        # Reset tooltip user
        self.tooltip_user = None
        
        # Do the rendering!
        self.renderitems = []
        for num, obj in enumerate(self.items):
            item, img = obj
            self.is_new_timeline(item)
            html = self.render_item(num, item, img)
            
            # Close Newest Container
            # <= beacause the ""firsttweet"" might get deleted
            # causing everything to be considered as new
            if item.id <= self.newest_id:
                html = '</div>' + html
            
            self.renderitems.insert(0, html)
        
        # Render
        self.set_html(self.renderitems)
    
    
    # HTML Helpers -------------------------------------------------------------
    def start(self):
        self.scroll.get_vscrollbar().set_value(0)
        self.offset_count = 0
        self.render_html("""
            <body class="unloaded" ondragstart="return false">
                <div class="loading"><img src="file://%s" /><br/>
                <b class="loadingtext">%s</b></div>
            </body>""" % (self.main.get_image(), self.lang_loading))
    
    def splash(self):
        self.scroll.get_vscrollbar().set_value(0)
        self.offset_count = 0
        self.render_html("""
            <body class="unloaded" ondragstart="return false">
                <div class="loading"><img src="file://%s" /><br/>
                <b class="loadingtext">%s</b></div>
            </body>""" % (self.main.get_image(), lang.html_welcome))
    
    def render_html(self, html):
        self.load_string("""
        <html>
        <head>
        <meta content="text/html; charset=UTF-8" http-equiv="content-type"/>
        <link rel="stylesheet" type="text/css" media="screen" href="file://%s"/>
        </head>
        %s
        </html>""" % (self.main.get_resource("atarashii.css"), html),
                        "text/html", "UTF-8", "file:///")
    
    def set_html(self, renderitems):
        self.main.gui.set_app_title()
        if len(self.items) > 0:
            self.render_html("""
                <body ondragstart="return false">
                    <div><div id="newcontainer">%s</div>
                    <div class="loadmore"><a href="more:%d"><b>%s</b></a></div>
                </body>""" % ("".join(renderitems),
                                self.items[0][0].id, self.lang_load))
        
        elif self.main.status(ST_LOGIN_SUCCESSFUL):
            self.render_html("""
                <body class="unloaded" ondragstart="return false">
                    <div class="loading"><b>%s</b></div>
                </body>""" % self.lang_empty)
    
    # The big magic spacer inserted... trust me it's really magic that this
    # thin does work at all...
    def insert_spacer(self, item, user, highlight, mentioned,
                    next_highlight = False, force = False):
        
        spacer = "foo"
        if item.id > self.init_id:
            # Name change
            if self.last_name != user.screen_name or self.new_timeline or force:
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
                    if next_highlight and self.last_highlight:
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
            if self.last_name != user.screen_name or self.new_timeline or force:
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
                    if next_highlight and self.last_highlight:
                        spacer = "" # Normal Gray
                    
                    elif next and self.last_mentioned:
                        spacer = "" # Normal Gray
                    
                    elif self.last_highlight:
                        spacer = "" # Normal Gray
                    
                    else:
                        spacer = "2" # Light Blue/White
        
        return '<div class="spacer%s"></div>' % spacer
    
    
    def avatar_html(self, user, num, img):
        return '''<a href="avatar:%d:http://twitter.com/%s">
                  <img width="32" src="file://%s" title="avatar" /></a>''' % (
                                      num, user.screen_name, img)
