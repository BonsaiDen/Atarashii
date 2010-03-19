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


# Sender Thread ----------------------------------------------------------------
# ------------------------------------------------------------------------------
import gobject
import threading

from constants import ST_SEND, ST_WAS_SEND, ST_WAS_RETWEET, ST_WAS_DELETE, \
                      ST_DELETE

from constants import MODE_TWEETS, MODE_MESSAGES, UNSET_TEXT, UNSET_ID_NUM

from utils import TweepError


# Send Tweets/Messages ---------------------------------------------------------
# ------------------------------------------------------------------------------
class Send(threading.Thread):
    def __init__(self, main, mode, text):
        threading.Thread.__init__(self)
        self.gui = main.gui
        self.main = main
        self.mode = mode
        self.text = text
    
    
    # Do a send ----------------------------------------------------------------
    def run(self):
        self.main.set_status(ST_WAS_SEND)
        try:
            if self.mode == MODE_TWEETS:
                self.send_tweet(self.text)
            
            elif self.mode == MODE_MESSAGES:
                self.send_message(self.text)
            
            else: # TODO implement search
                pass
            
            # Reset GUI
            gobject.idle_add(self.reset_gui)
        
        # Show Error Message
        except (IOError, TweepError), error:
            gobject.idle_add(self.main.handle_error, error)
        
        
        self.main.unset_status(ST_SEND)
    
    
    # Reset GUI ----------------------------------------------------------------
    def reset_gui(self):
        # Reply
        self.main.reply_user = UNSET_TEXT
        self.main.reply_text = UNSET_TEXT
        self.main.reply_id = UNSET_ID_NUM
        
        # Retweets
        self.main.retweet_user = UNSET_TEXT
        self.main.retweet_text = UNSET_TEXT
        
        # Message
        self.main.message_user = UNSET_TEXT
        self.main.message_id = UNSET_ID_NUM
        self.main.message_text = UNSET_TEXT
        
        # Reset Input
        self.gui.text.set_text(UNSET_TEXT)
        self.gui.show_input(False)
        if self.gui.mode == MODE_MESSAGES:
            self.gui.message.focus_me()
        
        elif self.gui.mode == MODE_TWEETS:
            self.gui.html.focus_me()
        
        else: # TODO implement search
            pass
        
        self.main.unset_status(ST_WAS_SEND)
    
    
    # Send a Tweet -------------------------------------------------------------
    # --------------------------------------------------------------------------
    def send_tweet(self, text):
        if self.main.reply_id != UNSET_ID_NUM:
            # Send Tweet
            update = self.main.api.update_status(text,
                                in_reply_to_status_id = self.main.reply_id)
            self.main.updater.set_last_tweet(update.id)
            
            # Insert temporary tweet
            imgfile = self.main.updater.get_image(update)
            self.gui.html.update_list.append((update, imgfile))
            gobject.idle_add(self.gui.html.push_updates)
        
        # Normal Tweet / Retweet
        else:
            # Send Tweet
            update = self.main.api.update_status(text)
            self.main.updater.set_last_tweet(update.id)
            
            # Insert temporary tweet
            imgfile = self.main.updater.get_image(update)
            self.gui.html.update_list.append((update, imgfile))
            gobject.idle_add(self.gui.html.push_updates)
    
    
    # Send a Direct Message ----------------------------------------------------
    # --------------------------------------------------------------------------
    def send_message(self, text):
        # Send Message
        if self.main.message_id != UNSET_ID_NUM:
            message = self.main.api.send_direct_message(text = text,
                                        user_id = self.main.message_id)
        
        else:
            message = self.main.api.send_direct_message(text = text,
                                        screen_name = self.main.message_user)
        
        self.main.updater.set_last_message(message.id)
        
        # Insert temporary message
        imgfile = self.main.updater.get_image(message, True)
        self.gui.message.update_list.append((message, imgfile))
        gobject.idle_add(self.gui.message.push_updates)



# New style Retweets -----------------------------------------------------------
# ------------------------------------------------------------------------------
class Retweet(threading.Thread):
    def __init__(self, main, name, tweet_id):
        threading.Thread.__init__(self)
        self.gui = main.gui
        self.main = main
        self.name = name
        self.tweet_id = tweet_id
    
    def run(self):
        self.main.set_status(ST_WAS_SEND)
        self.main.set_status(ST_WAS_RETWEET)
        try:
            # Retweet
            self.main.api.retweet(self.tweet_id)
            
            # Focus HTML
            self.gui.show_input(False)
            if self.gui.mode == MODE_MESSAGES:
                self.gui.message.focus_me()
            
            elif self.gui.mode == MODE_TWEETS:
                self.gui.html.focus_me()
            
            else: # TODO implement search
                pass
            
            self.main.unset_status(ST_WAS_SEND)
            gobject.idle_add(self.gui.show_retweet_info, self.name)
        
        except (IOError, TweepError), error:
            gobject.idle_add(self.main.handle_error, error)
        
        self.main.unset_status(ST_SEND)


# Deletes ----------------------------------------------------------------------
# ------------------------------------------------------------------------------
class Delete(threading.Thread):
    def __init__(self, main, tweet_id, message_id):
        threading.Thread.__init__(self)
        self.gui = main.gui
        self.main = main
        self.tweet_id = tweet_id
        self.message_id = message_id
    
    def run(self):
        self.main.set_status(ST_WAS_DELETE)
        try:
            # Delete
            if self.tweet_id != UNSET_ID_NUM:
                self.main.api.destroy_status(self.tweet_id)
            
            elif self.message_id != UNSET_ID_NUM:
                self.main.api.destroy_direct_message(self.message_id)
            
            # Focus HTML
            self.gui.show_input(False)
            if self.gui.mode == MODE_MESSAGES:
                self.gui.message.focus_me()
            
            elif self.gui.mode == MODE_TWEETS:
                self.gui.html.focus_me()
            
            else: # TODO implement search
                pass
            
            self.main.unset_status(ST_WAS_DELETE)
            
            # Remove from view!
            if self.tweet_id != UNSET_ID_NUM:
                gobject.idle_add(self.gui.html.remove, self.tweet_id)
                
            elif self.message_id != UNSET_ID_NUM:
                gobject.idle_add(self.gui.message.remove, self.message_id)
            
            # Show Info
            gobject.idle_add(self.gui.show_delete_info,
                             self.tweet_id, self.message_id)
        
        except (IOError, TweepError), error:
            gobject.idle_add(self.main.handle_error, error)
        
        self.main.unset_status(ST_DELETE)
        
        
# Favorites --------------------------------------------------------------------
# ------------------------------------------------------------------------------
class Favorite(threading.Thread):
    def __init__(self, main, tweet_id, mode, name):
        threading.Thread.__init__(self)
        self.gui = main.gui
        self.main = main
        self.tweet_id = tweet_id
        self.mode = mode
        self.name = name
    
    def run(self):
        try:
            # Create Favorite
            if self.mode:
                self.main.api.create_favorite(self.tweet_id)
            
            # Destroy it
            else:
                self.main.api.destroy_favorite(self.tweet_id)
            
            gobject.idle_add(self.gui.html.favorite, self.tweet_id, self.mode)
        
        except (IOError, TweepError), error:
            print error
            gobject.idle_add(self.gui.show_favorite_error, self.name, self.mode)

        del self.main.favorites_pending[self.tweet_id]

