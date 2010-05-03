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
    def get_init_tweets(self, last=False, init=False):
        updates = []
        try:
            updates = self.try_get_items(self.get_updates,
                                         self.tweet.get_first())
            
            if init:
                self.gui.progress_step()
        
        except (IOError, TweepError), error:
            gobject.idle_add(self.main.on_login_failed, error)
            return False
        
        if len(updates) > 0:
            self.tweet.save_last_id(updates[0].id)
        
        # Expand the tweet count
        if len(updates) > self.main.max_tweet_count:
            self.main.max_tweet_count = len(updates)
            
            # Hard limit
            if self.main.max_tweet_count > self.main.max_tweet_init_count:
                self.main.max_tweet_count = self.main.max_tweet_init_count
        
        updates.reverse()
        for i in updates:
            if i is not None:
                self.notified_tweets.append(i.id)
                self.tweet.update_list.append([i, self.get_image(i)])
        
        gobject.idle_add(self.do_render, self.tweet, init, last)
        return True
    
    
    # Don't call this directly! Use updater.try_get_items instead --------------
    # --------------------------------------------------------------------------
    def get_updates(self, since_id, max_id, max_count):
        gobject.idle_add(self.gui.update_status, True)
        updates = []
        mentions = []
        if since_id != HTML_UNSET_ID:
            if max_id is None:
                updates = self.api.home_timeline(since_id = since_id,
                                                 count = max_count)
                
                if len(updates) > 0:
                    since_id = updates[len(updates) - 1].id
                
                mentions = self.api.mentions(since_id = since_id,
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
        
        self.update_limit()
        updates = updates + mentions
        updates.sort(key = lambda u: u.id, reverse = True)
        
        # find the last mention, why do we do this?
        # sometimes the mention arrives before the reply
        # but we want to replace the mention when the accomponing reply comens
        # in so we need to request from mention.id - 1, instead of the last_id
        current_mention = self.last_mention_id
        self.last_mention_id = HTML_UNSET_ID
        for e in updates:
            if hasattr(e, 'is_mentioned') and e.is_mentioned \
               and e.id > current_mention:
                
                self.last_mention_id = e.id - 1
                
                # and check if a reply exists
                for i in updates:
                    if not hasattr(i, 'is_mentioned') and i.id == e.id:
                        self.last_mention_id = HTML_UNSET_ID
                        break
                
                break
        
        return updates
    
    # Tweet History
    def load_history(self):
        updates = []
        try:
            if self.tweet.history_level < 2:
                load_count = self.main.load_tweet_count
            
            elif self.tweet.history_level < 4:
                load_count = self.main.load_tweet_count * 1.5
            
            else:
                load_count = self.main.load_tweet_count * 2
            
            updates = self.try_get_items(
                           self.get_updates,
                           max_id = self.tweet.load_history_id,
                           max_count = load_count)
        
        except (IOError, TweepError), error:
            self.tweet.load_history_id = HTML_UNSET_ID
            self.main.unset_status(ST_HISTORY)
            gobject.idle_add(self.main.handle_error, error)
            gobject.idle_add(self.gui.set_multi_button, True)
            return False
        
        self.main.max_tweet_count += len(updates)
        for i in updates:
            imgfile = self.get_image(i)
            self.tweet.history_list.append((i, imgfile))
        
        self.tweet.load_history_id = HTML_UNSET_ID
        self.main.unset_status(ST_HISTORY | ST_NETWORK_FAILED)
        
        def update_view():
            self.tweet.push_updates()
            self.gui.show_input()
            self.gui.set_multi_button(True)
        
        gobject.idle_add(update_view)

