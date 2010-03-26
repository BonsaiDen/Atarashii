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


# Background Twitter Updater / Messages ----------------------------------------
# ------------------------------------------------------------------------------
import gobject

from utils import TweepError

from constants import ST_HISTORY, ST_NETWORK_FAILED
from constants import HTML_UNSET_ID


class UpdaterMessage:
    # Set lastest Message
    def set_last_message(self, item_id):
        self.message.last_id = item_id
        self.settings['lastmessage_' + self.main.username] = item_id
        if len(self.message.items) > 0:
            self.message.newest_id = self.message.items[
                                     len(self.message.items) - 1][0].id
    
    
    # Load initial messages ----------------------------------------------------
    def get_init_messages(self, last=False, init=False):
        messages = []
        try:
            messages = self.try_get_items(self.get_messages,
                                          self.message.get_first())
        
        except (IOError, TweepError), error:
            gobject.idle_add(self.main.on_login_failed, error)
            return False
        
        if len(messages) > 0:
            self.set_last_message(messages[0].id)
        
        messages.reverse()
        for i in messages:
            self.message.update_list.append((i, self.get_image(i, True)))
        
        gobject.idle_add(self.do_render, self.message, init, last)
        return True
    
    
    # Main Function that fetches the messages ----------------------------------
    def get_messages(self, since_id=0, max_id=None, max_count=200):
        messages = []
        if since_id != HTML_UNSET_ID:
            if max_id is None:
                messages = self.api.direct_messages(since_id = since_id,
                                                    count = max_count)
                
                messages += self.api.sent_direct_messages(since_id = since_id,
                                                          count = max_count)
            
            else:
                messages = self.api.direct_messages(max_id = max_id,
                                                    count = max_count)
                
                messages += self.api.sent_direct_messages(max_id = max_id,
                                                          count = max_count)
        
        else:
            messages = self.api.direct_messages(
                                count = self.main.load_message_count // 2)
            
            messages += self.api.sent_direct_messages(
                                 count = self.main.load_message_count // 2)
        
        self.refresh_messages = False
        self.update_limit()
        return messages
    
    # Message History
    def load_history_message(self):
        messages = []
        try:
            messages = self.try_get_items(
                            self.get_messages,
                            max_id = self.message.load_history_id,
                            max_count = self.main.load_message_count)
        
        except (IOError, TweepError), error:
            self.message.load_history_id = HTML_UNSET_ID
            self.main.unset_status(ST_HISTORY)
            gobject.idle_add(self.main.handle_error, error)
            return False
        
        self.main.max_message_count += len(messages)
        for i in messages:
            imgfile = self.get_image(i, True)
            self.message.history_list.append((i, imgfile))
        
        self.message.load_history_id = HTML_UNSET_ID
        self.main.unset_status(ST_HISTORY | ST_NETWORK_FAILED)
        
        if len(messages) > 0:
            self.message.load_history = True
            self.message.history_loaded = True
            self.message.history_count += len(messages)
            
        def update_view():
            self.message.push_updates()
            self.gui.show_input()
            self.gui.set_refresh_update(True)
        
        gobject.idle_add(update_view)

