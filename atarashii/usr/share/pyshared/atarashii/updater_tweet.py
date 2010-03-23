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


# Background Twitter Updater / Tweets ------------------------------------------
# ------------------------------------------------------------------------------
import gobject

from utils import TweepError

from constants import ST_HISTORY, ST_NETWORK_FAILED
from constants import HTML_UNSET_ID, HTML_LOADED


class UpdaterTweet:
    def __init__(self):
        pass
    
    # Set lastest Tweet
    def set_last_tweet(self, item_id):
        self.html.last_id = item_id
        self.settings['lasttweet_' + self.main.username] = item_id
        if len(self.html.items) > 0:
            self.html.newest_id = self.html.items[
                                  len(self.html.items) - 1][0].id
    
    # Load initial tweets ------------------------------------------------------
    def get_init_tweets(self, last = False, init = False):
        updates = []
        try:
            updates = self.try_get_updates(self.html.get_first())
        
        except (IOError, TweepError), error:
            gobject.idle_add(self.main.on_login_failed, error)
            return False
        
        if len(updates) > 0:
            self.set_last_tweet(updates[0].id)
        
        updates.reverse()
        for i in updates:
            if i != None:
                imgfile = self.get_image(i)
                self.html.update_list.append((i, imgfile))
        
        def render():
            self.html.push_updates()
            self.html.load_state = HTML_LOADED
            
            # Finish the login
            if init:
                self.started = True
                gobject.idle_add(self.main.on_login)
                gobject.idle_add(self.gui.set_refresh_update, True)
            
            # Show login message
            if last:
                gobject.idle_add(self.main.show_start_notifications)
        
        gobject.idle_add(render)
        return True
    
    # Main Function that fetches the updates -----------------------------------
    # --------------------------------------------------------------------------
    def try_get_updates(self, since_id = 0, max_id = None, max_count = 200):
        count = 0
        while True:
            count += 1
            try:
                # Try to get the updates and then break
                return self.get_updates(since_id = since_id, max_id = max_id,
                                max_count = max_count)
            
            # Stop immediately on network error
            except IOError, error:
                raise error
            
            # Something went wrong, either try it again or break with the error
            except TweepError, error:
                if count == 2:
                    raise error
            
            # Failsafe
            except:
                return []
    
    # Tweets
    def get_updates(self, since_id = 0, max_id = None, max_count = 200):
        gobject.idle_add(self.gui.update_status, True)
        updates = []
        mentions = []
        if since_id != HTML_UNSET_ID:
            if max_id == None:
                mentions = self.api.mentions(since_id = since_id,
                                             count = max_count)
                
                updates = self.api.home_timeline(since_id = since_id,
                                                 count = max_count)
            
            else:
                updates = self.api.home_timeline(
                                   max_id = max_id,count = max_count)
                
                if len(updates) > 0:
                    mentions = self.api.mentions(
                                        max_id = max_id,
                                        since_id = updates[len(updates) - 1].id,
                                        count = max_count)
        
        else:
            updates = self.api.home_timeline(count = self.main.load_tweet_count)
            if len(updates) > 0:
                mentions = self.api.mentions(
                                    since_id = updates[len(updates) - 1].id,
                                    count = 200)
        
        for i in mentions:
            i.is_mentioned = True
        
        self.refresh_now = False
        self.update_limit()
        updates = updates + mentions
        if len(mentions) > 0:
            return self.process_updates(updates)
        
        else:
            return updates
    
    # Tweet History
    def load_history(self):
        updates = []
        try:
            updates = self.try_get_updates(max_id = self.html.load_history_id,
                                        max_count = self.main.load_tweet_count)
        
        except (IOError, TweepError), error:
            self.html.load_history_id = HTML_UNSET_ID
            self.main.unset_status(ST_HISTORY)
            gobject.idle_add(self.main.handle_error, error)
            return False
        
        self.main.max_tweet_count += len(updates)
        for i in updates:
            imgfile = self.get_image(i)
            self.html.history_list.append((i, imgfile))
        
        self.html.load_history_id = HTML_UNSET_ID
        self.main.unset_status(ST_HISTORY | ST_NETWORK_FAILED)
        
        if len(updates) > 0:
            self.html.load_history = True
            self.html.history_loaded = True
            self.html.history_count += len(updates)
        
        def update_view():
            self.html.push_updates()
            self.gui.show_input()
            self.gui.set_refresh_update(True)
        
        gobject.idle_add(update_view)

