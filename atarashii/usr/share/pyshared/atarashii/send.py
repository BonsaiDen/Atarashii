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


# API Call Threads -------------------------------------------------------------
# ------------------------------------------------------------------------------
import gobject
import threading

from utils import TweepError

from constants import MODE_TWEETS, MODE_MESSAGES, UNSET_TEXT, UNSET_ID_NUM
from constants import ST_SEND, ST_WAS_SEND, ST_WAS_RETWEET, ST_WAS_DELETE, \
                      ST_DELETE, ST_NETWORK_FAILED


# Send/Edit base class ---------------------------------------------------------
# ------------------------------------------------------------------------------
class APICall(threading.Thread):
    def __init__(self, main, text, multi=False):
        threading.Thread.__init__(self)
        self.gui = main.gui
        self.main = main
        self.text = text
        self.multi = multi
        self.daemon = True
        self.start()
    
    def run(self):
        self.main.unset_status(ST_NETWORK_FAILED)
        if self.before():
            try:
                self.call()
                
                # Reset the GUI
                if not self.multi:
                    self.main.unset('reply', 'retweet', 'edit', 'message')
                    gobject.idle_add(self.gui.text.set_text, UNSET_TEXT)
                    gobject.idle_add(self.gui.show_input, False, True)
                
                elif self.main.reply_user != UNSET_TEXT:
                    gobject.idle_add(self.gui.show_input, False, True)
                    gobject.idle_add(self.gui.text.reply, True)
                
                elif self.main.message_user != UNSET_TEXT:
                    gobject.idle_add(self.gui.show_input, False, True)
                    gobject.idle_add(self.gui.text.message, True)
                
                else:
                    gobject.idle_add(self.gui.text.set_text, UNSET_TEXT)
                    gobject.idle_add(self.gui.show_input, False, True)
                    gobject.idle_add(self.gui.text.grab_focus)
                
                self.main.unset_status(ST_WAS_SEND)
            
            except (IOError, TweepError), error:
                self.on_error()
                gobject.idle_add(self.main.handle_error, error)
            
            self.main.unset_status(ST_SEND)
    
    def on_error(self):
        pass
    
    def after_send(self):
        pass
    
    def send_tweet(self, text, reply_id):
        if reply_id != UNSET_ID_NUM:
            update = self.main.api.update_status(text,
                                   in_reply_to_status_id = reply_id)
        
        else:
            update = self.main.api.update_status(text)
        
        self.after_send()
        self.gui.html.set_newest()
        
        imgfile = self.main.updater.get_image(update)
        self.gui.html.update_list.append([update, imgfile])
        gobject.idle_add(self.gui.html.push_updates)


# Send Tweets/Messages ---------------------------------------------------------
# ------------------------------------------------------------------------------
class Send(APICall):
    def before(self):
        self.mode = self.main.gui.mode
        self.main.set_status(ST_WAS_SEND)
        return True
    
    def call(self):
        if self.mode == MODE_TWEETS:
            self.send_tweet(self.text, self.main.reply_id)
        
        elif self.mode == MODE_MESSAGES:
            self.send_message(self.text)
    
    def send_message(self, text):
        if self.main.message_user_id != UNSET_ID_NUM:
            message = self.main.api.send_direct_message(text = text,
                                    user_id = self.main.message_user_id)
        
        else:
            message = self.main.api.send_direct_message(text = text,
                                    screen_name = self.main.message_user)
        
        self.gui.message.set_newest()
        imgfile = self.main.updater.get_image(message, True)
        self.gui.message.update_list.append([message, imgfile])
        gobject.idle_add(self.gui.message.push_updates)


# Edit Tweets ------------------------------------------------------------------
# ------------------------------------------------------------------------------
class Edit(APICall):
    def before(self):
        self.tweet_id = self.main.edit_id
        if not self.delete():
            self.main.unset_status(ST_SEND)
            return False
        
        else:
            self.main.set_status(ST_WAS_SEND)
            return True
    
    def call(self):
        self.send_tweet(self.text, self.main.edit_reply_id)
    
    def on_error(self):
        gobject.idle_add(self.gui.html.remove, self.tweet_id)
    
    def after_send(self):
        gobject.idle_add(self.gui.html.remove, self.tweet_id)
    
    def delete(self):
        self.main.set_status(ST_WAS_DELETE)
        try:
            self.main.api.destroy_status(self.tweet_id)
            self.main.unset_status(ST_WAS_DELETE)
        
        except (IOError, TweepError), error:
            gobject.idle_add(self.main.handle_error, error)
            return False
        
        self.main.unset_status(ST_DELETE)
        return True


# Simple call base class -------------------------------------------------------
# ------------------------------------------------------------------------------
class SimpleAPICall(threading.Thread):
    def __init__(self, main, *args):
        threading.Thread.__init__(self)
        self.main = main
        self.args = args
        self.daemon = True
        self.start()
    
    def run(self):
        self.before(self.main, *self.args)
        try:
            self.call(self.main, *self.args)
            self.on_success(self.main, *self.args)
        
        except (IOError, TweepError), error:
            self.error = error
            self.on_error(self.main, *self.args)
        
        self.after(self.main, *self.args)
    
    def before(self, *args):
        pass
    
    def on_sucess(self, *args):
        pass
    
    def on_error(self, *args):
        pass
    
    def after(self, *args):
        pass


# New style Retweets -----------------------------------------------------------
# ------------------------------------------------------------------------------
class Retweet(SimpleAPICall):
    def before(self, main, name, tweet_id):
        main.set_status(ST_WAS_SEND)
        main.set_status(ST_WAS_RETWEET)
    
    def call(self, main, name, tweet_id):
        main.api.retweet(tweet_id)
    
    def on_success(self, main, name, tweet_id):
        main.unset_status(ST_WAS_SEND)
        main.gui.show_input(False, True)
        gobject.idle_add(main.gui.show_retweet_info, name)
    
    def on_error(self, main, name, tweet_id):
        gobject.idle_add(main.handle_error, self.error)
    
    def after(self, main, name, tweet_id):
        main.unset_status(ST_SEND)
        gobject.idle_add(main.gui.update_status, True)


# Deletes ----------------------------------------------------------------------
# ------------------------------------------------------------------------------
class Delete(SimpleAPICall):
    def before(self, main, tweet_id, message_id):
        main.set_status(ST_WAS_DELETE)
    
    def call(self, main, tweet_id, message_id):
        if tweet_id != UNSET_ID_NUM:
            main.api.destroy_status(tweet_id)
        
        elif message_id != UNSET_ID_NUM:
            main.api.destroy_direct_message(message_id)
    
    def on_success(self, main, tweet_id, message_id):
        main.unset_status(ST_WAS_DELETE)
        main.gui.show_input(False, True)
        
        if tweet_id != UNSET_ID_NUM:
            gobject.idle_add(main.gui.html.remove, tweet_id)
            main.delete_tweet_id = UNSET_ID_NUM
        
        elif message_id != UNSET_ID_NUM:
            gobject.idle_add(main.gui.message.remove, message_id)
            main.delete_message_id = UNSET_ID_NUM
        
        gobject.idle_add(main.gui.show_delete_info, tweet_id, message_id)
    
    def on_error(self, main, tweet_id, message_id):
        gobject.idle_add(main.handle_error, self.error)
    
    def after(self, main, tweet_id, message_id):
        main.unset_status(ST_DELETE)
        gobject.idle_add(main.gui.update_status, True)


# Favorites --------------------------------------------------------------------
# ------------------------------------------------------------------------------
class Favorite(SimpleAPICall):
    def call(self, main, tweet_id, mode, name):
        if mode:
            main.api.create_favorite(tweet_id)
        
        else:
            main.api.destroy_favorite(tweet_id)
    
    def on_success(self, main, tweet_id, mode, name):
        gobject.idle_add(main.gui.html.favorite, tweet_id, mode)
    
    def on_error(self, main, tweet_id, mode, name):
        gobject.idle_add(main.gui.show_favorite_error, mode, name)
    
    def after(self, main, tweet_id, mode, name):
        del main.favorites_pending[tweet_id]


# Friend information -----------------------------------------------------------
# ------------------------------------------------------------------------------
class Friends(SimpleAPICall):
    def before(self, main, name, menu, callback):
        self.menu = menu
    
    def call(self, main, name, menu, callback):
        self.friend = self.main.api.show_friendship(target_screen_name = name)
    
    def on_success(self, main, name, menu, callback):
        if self.menu is not None:
            gobject.idle_add(callback, self.menu, self.friend)


# Profile ----------------------------------------------------------------------
# ------------------------------------------------------------------------------
class Profile(SimpleAPICall):
    def call(self, main, name, callback):
        self.user = self.main.api.get_user(screen_name = name)
        self.friend = self.main.api.show_friendship(target_screen_name = name)
    
    def on_success(self, main, name, callback):
        gobject.idle_add(callback, self.user, self.friend)

    def on_error(self, main, name, callback):
        gobject.idle_add(main.stop_profile)
        gobject.idle_add(main.gui.show_profile_error, name)


# Follow -----------------------------------------------------------------------
# ------------------------------------------------------------------------------
class Follow(SimpleAPICall):
    def call(self, main, user_id, name, mode):
        if mode:
            main.api.create_friendship(user_id = user_id)
        
        else:
            main.api.destroy_friendship(user_id = user_id)
    
    def on_success(self, main, user_id, name, mode):
        gobject.idle_add(main.gui.show_follow_info, mode, name)
    
    def on_error(self, main, user_id, name, mode):
        gobject.idle_add(main.gui.show_follow_error, mode, name)
    
    def after(self, main, user_id, name, mode):
        del main.follow_pending[name.lower()]


# Block ------------------------------------------------------------------------
# ------------------------------------------------------------------------------
class Block(SimpleAPICall):
    def call(self, main, user_id, name, mode):
        if mode:
            main.api.create_block(user_id = user_id)
        
        else:
            main.api.destroy_block(user_id = user_id)
    
    def on_success(self, main, user_id, name, mode):
        gobject.idle_add(main.gui.show_block_info, mode, name)
    
    def on_error(self, main, user_id, name, mode):
        gobject.idle_add(main.gui.show_block_error, mode, name)
    
    def after(self, main, user_id, name, mode):
        del main.block_pending[name.lower()]

