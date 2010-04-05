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
from constants import HTML_UNSET_ID


class UpdaterTweet(object):
    
    # Load initial tweets ------------------------------------------------------
    def get_init_tweets(self, last=False, init=False):
        updates = []
        try:
            updates = self.try_get_items(self.get_updates,
                                         self.html.get_first())
        
        except (IOError, TweepError), error:
            gobject.idle_add(self.main.on_login_failed, error)
            return False
        
        if len(updates) > 0:
            self.html.save_last_id(updates[0].id)
        
        # Expand the tweet count
        if len(updates) > self.main.max_tweet_count:
            self.main.max_tweet_count = len(updates)
            
            # Hard limit
            if self.main.max_tweet_count > self.main.max_tweet_init_count:
                self.main.max_tweet_count = self.main.max_tweet_init_count
        
        updates.reverse()
        for i in updates:
            if i is not None:
                self.html.update_list.append((i, self.get_image(i)))
        
        gobject.idle_add(self.do_render, self.html, init, last)
        return True
    
    
    # Main Function that fetches the updates -----------------------------------
    # Don't call this directly! Use updater.try_get_items instead
    def get_updates(self, since_id, max_id, max_count):
        gobject.idle_add(self.gui.update_status, True)
        updates = []
        mentions = []
        if since_id != HTML_UNSET_ID:
            if max_id is None:
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
        return updates
    
    # Tweet History
    def load_history(self):
        updates = []
        try:
            updates = self.try_get_items(
                           self.get_updates,
                           max_id = self.html.load_history_id,
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
            self.gui.set_multi_button(True)
        
        gobject.idle_add(update_view)

