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


class UpdaterProfile(object):
    
    
    # Don't call this directly! Use updater.try_get_items instead --------------
    # --------------------------------------------------------------------------
    def get_profile(self, since_id, max_id, max_count):
        gobject.idle_add(self.gui.update_status, True)
        updates = []
        if since_id != HTML_UNSET_ID:
            if max_id is None:
                updates = self.api.user_timeline(
                               screen_name = self.main.profile_current_user,
                               since_id = since_id, count = max_count)
            
            else:
                updates = self.api.user_timeline(
                                   screen_name = self.main.profile_current_user,
                                   max_id = max_id,count = max_count)
        
        else:
            updates = self.api.user_timeline(
                               screen_name = self.main.profile_current_user,
                               count = self.main.load_tweet_count)
        
        self.update_limit()
        updates.sort(key = lambda u: u.id, reverse = True)
        return updates
    
    # Profile History
    def load_history_profile(self):
        self.gui.load_button.box.set_sensitive(False)
        
        updates = []
        try:
            if self.profile.history_level < 2:
                load_count = self.main.load_profile_count
            
            elif self.profile.history_level < 4:
                load_count = self.main.load_profile_count * 1.5
            
            else:
                load_count = self.main.load_profile_count * 2
            
            updates = self.try_get_items(
                           self.get_profile,
                           max_id = self.profile.load_history_id,
                           max_count = load_count)
        
        except (IOError, TweepError), error:
            self.profile.load_history_id = HTML_UNSET_ID
            self.main.unset_status(ST_HISTORY)
            gobject.idle_add(self.main.handle_error, error)
            self.gui.load_button.box.set_sensitive(True)
            gobject.idle_add(self.gui.set_multi_button, False)
            return False
        
      #  self.main.max_tweet_count += len(updates)
        for i in updates:
            img_file = self.get_image(i)
            self.profile.history_list.append((i, img_file))
        
        self.profile.load_history_id = HTML_UNSET_ID
        self.main.unset_status(ST_HISTORY | ST_NETWORK_FAILED)
        
        def update_view():
            self.profile.push_updates(True)
            self.gui.show_input()
            self.gui.load_button.box.set_sensitive(True)
            self.gui.set_multi_button(False)
        
        gobject.idle_add(update_view)

