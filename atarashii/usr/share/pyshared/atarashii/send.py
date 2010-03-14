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
import sys

from constants import MODE_TWEETS, MODE_MESSAGES, UNSET_TEXT, UNSET_ID_NUM


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
        self.main.was_sending = True
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
        except Exception, error:
            gobject.idle_add(lambda: self.gui.show_error(error))
        
        
        self.main.is_sending = False
    
    
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
            self.gui.message.grab_focus()
        
        elif self.gui.mode == MODE_TWEETS:
            self.gui.html.grab_focus()
            
        else: # TODO implement search
            pass
        
        self.main.was_sending = False
    
    
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
            gobject.idle_add(lambda: self.gui.html.push_updates())
            
        # Normal Tweet / Retweet
        else:
            # Send Tweet
            update = self.main.api.update_status(text)
            self.main.updater.set_last_tweet(update.id)
        
            # Insert temporary tweet
            imgfile = self.main.updater.get_image(update)
            self.gui.html.update_list.append((update, imgfile))
            gobject.idle_add(lambda: self.gui.html.push_updates())
    
    
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
        gobject.idle_add(lambda: self.gui.message.push_updates())


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
        self.main.was_sending = True
        self.main.was_retweeting = True
        try:
            # Retweet
            self.main.api.retweet(self.tweet_id)
        
            # Focus HTML
            self.gui.show_input(False)
            if self.gui.mode == MODE_MESSAGES:
                self.gui.message.grab_focus()
            
            elif self.gui.mode == MODE_TWEETS:
                self.gui.html.grab_focus()
                
            else: # TODO implement search
                pass
            
            self.main.was_sending = False
            gobject.idle_add(lambda: self.gui.show_retweet_info(self.name))
            
        except Exception, error:
            gobject.idle_add(lambda: self.gui.show_error(error))
        
        self.main.is_sending = False

