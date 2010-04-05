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


# Background Twitter Updater ---------------------------------------------------
# ------------------------------------------------------------------------------
import time
import threading
import urllib
import os
import gobject
import calendar
import socket

from language import LANG as lang
from settings import HOME_DIR
from utils import tweepy, TweepError
from updater_message import UpdaterMessage
from updater_tweet import UpdaterTweet

from constants import ST_WARNING_RATE, ST_UPDATE, ST_LOGIN_COMPLETE, \
                      ST_NETWORK_FAILED

from constants import MODE_MESSAGES, MODE_TWEETS, HTML_UNSET_ID, \
                      UNSET_TIMEOUT, HTML_RESET, HTML_LOADING, HTML_LOADED


class Updater(threading.Thread, UpdaterMessage, UpdaterTweet):
    def __init__(self, main):
        threading.Thread.__init__(self)
        self.main = main
        self.settings = main.settings
        self.gui = None
        self.api = None
        self.html = None
        self.message = None
        
        # Notifier
        self.notifier = self.main.notifier
        
        # Variables
        self.running = True
        self.started = False
        self.do_init = False
        self.refresh_now = False
        self.refresh_messages = False
        
        self.load_history_id = HTML_UNSET_ID
        self.load_history_message_id = HTML_UNSET_ID
        self.ratelimit = 150
        self.message_counter = 0
        self.finish = False
        
        self.daemon = True
        self.wait = threading.Event()
        self.password_wait = threading.Event()
    
    
    # Init the Updater ---------------------------------------------------------
    # --------------------------------------------------------------------------
    def init(self):
        self.gui = self.main.gui
        
        # Init Views
        self.html = self.gui.html
        self.message = self.gui.message
        
        # Reset
        self.finish = False
        self.message_counter = 0
        self.do_init = False
        self.started = False
        self.refresh_now = False
        self.main.refresh_time = UNSET_TIMEOUT
        self.main.refresh_timeout = UNSET_TIMEOUT
        self.html.load_history_id = HTML_UNSET_ID
        self.message.load_history_id = HTML_UNSET_ID
        
        self.message.last_id = HTML_UNSET_ID
        self.html.last_id = HTML_UNSET_ID
        self.message.load_state = HTML_RESET
        self.html.load_state = HTML_RESET
        
        # InitID = the last read tweet
        self.html.init_id = self.html.get_latest()
        self.message.init_id = self.message.get_latest()
        
        # Try to Login
        auth = self.login()
        if not auth:
            return False
        
        self.api = self.main.api = tweepy.API(auth)
        self.init_load()
    
    
    # Login --------------------------------------------------------------------
    # --------------------------------------------------------------------------
    def login(self):
        # xAuth Login, yes the app stuff is here, were else should it go?
        # Why should anyone else use the Atarashii App for posting from HIS
        # client? :D
        auth = tweepy.OAuthHandler('PYuZHIEoIGnNNSJb7nIY0Q',
                                   'Fw91zqMpMECFMJkdM3SFM7guFBGiFfkDRu0nDOc7tg',
                                   secure = True)
        
        try:
            # Try using an old token
            token_ok = False
            key_name = 'xkey_' + self.main.username
            secret_name = 'xsecret_' + self.main.username
            if self.settings.isset(key_name) \
               and self.settings.isset(secret_name):
                auth.set_access_token(self.settings[key_name],
                                      self.settings[secret_name])
                
                try:
                    auth.get_username()
                    token_ok = True
                
                except IOError, error:
                    raise error
                
                except TweepError, error:
                    self.settings[key_name] = ''
                    self.settings[secret_name] = ''
            
            # Get a new token!
            if not token_ok:
                gobject.idle_add(self.gui.force_show)
                gobject.idle_add(self.gui.enter_password)
                
                # Wait for password entry
                self.password_wait.clear()
                self.password_wait.wait()
                
                # Try to login with the new password
                if self.main.api_temp_password != '':
                    token = auth.get_xauth_access_token(
                                 self.main.username,
                                 self.main.api_temp_password)
                    
                    self.main.api_temp_password = None
                    self.settings[key_name] = token.key
                    self.settings[secret_name] = token.secret
                
                else:
                    gobject.idle_add(self.main.on_login_failed)
                    self.main.api_temp_password = None
                    return False
        
        except (IOError, TweepError), error:
            self.main.api_temp_password = None
            gobject.idle_add(self.main.on_network_failed, error)
            return False
        
        return auth
    
    
    # Initial Load -------------------------------------------------------------
    # --------------------------------------------------------------------------
    def init_load(self):
        # Set loading to pending
        self.message.load_state = HTML_LOADING
        self.html.load_state = HTML_LOADING
        
        # Lazy loading
        if self.gui.mode == MODE_MESSAGES:
            if not self.get_init_messages(init = True):
                self.message.load_state = HTML_RESET
                self.html.load_state = HTML_RESET
                return
        
        elif self.gui.mode == MODE_TWEETS:
            if not self.get_init_tweets(init = True):
                self.message.load_state = HTML_RESET
                self.html.load_state = HTML_RESET
                return
        
        else: # TODO implement loading of search
            pass
        
        # Load other stuff
        if self.gui.mode == MODE_TWEETS:
            if self.get_init_messages(True):
                if self.gui.mode == MODE_MESSAGES:
                    gobject.idle_add(self.gui.show_input)
                
                else:
                    gobject.idle_add(self.gui.set_multi_button, True)
            
            else:
                self.message.load_state = HTML_RESET
                self.html.load_state = HTML_RESET
                return
        
        elif self.gui.mode == MODE_MESSAGES:
            if self.get_init_tweets(True):
                if self.gui.mode == MODE_TWEETS:
                    gobject.idle_add(self.gui.show_input)
                
                else:
                    gobject.idle_add(self.gui.set_multi_button, True)
            
            else:
                self.message.load_state = HTML_RESET
                self.html.load_state = HTML_RESET
                return
        
        else: # TODO implement loading of search
            pass
        
        # Force Title Update
        self.main.set_status(ST_LOGIN_COMPLETE)
        gobject.idle_add(self.gui.set_app_title)
        if self.gui.settings_dialog is not None:
            gobject.idle_add(self.gui.settings_dialog.activate, True)
        
        # Init Timer
        gobject.idle_add(self.main.save_settings, True)
        self.main.refresh_time = calendar.timegm(time.gmtime())
        gobject.idle_add(self.gui.set_multi_button, True)
    
    
    # Mainloop -----------------------------------------------------------------
    # --------------------------------------------------------------------------
    def run(self):
        while self.running:
            if self.do_init:
                self.init()
            
            elif self.started:
                if self.finish:
                    self.finish = False
                    self.end_update()
                
                elif self.html.load_history_id != HTML_UNSET_ID:
                    self.load_history()
                
                elif self.message.load_history_id != HTML_UNSET_ID:
                    self.load_history_message()
                
                elif self.main.refresh_timeout != UNSET_TIMEOUT:
                    self.check_for_update()
            
            self.wait.clear()
            gobject.timeout_add(1000, self.unwait)
            self.wait.wait()
    
    def unwait(self, init=False, tweets=False, messages=False):
        if init:
            self.do_init = True
        
        if tweets:
            self.refresh_now = True
            
        if messages:
            self.refresh_messages = True
        
        self.wait.set()
    
    def check_for_update(self):
        if self.main.refresh_time == UNSET_TIMEOUT:
            return False
        
        elif calendar.timegm(time.gmtime()) > self.main.refresh_time \
           + self.main.refresh_timeout or self.refresh_now \
           or self.refresh_messages:
            
            self.refresh_messages = False
            self.refresh_now = False
            self.main.set_status(ST_UPDATE)
            gobject.idle_add(self.gui.set_multi_button, False, None, True, True)
            self.update()
            return True
    
    def end_update(self):
        gobject.idle_add(self.main.save_settings, True)
        self.main.unset_status(ST_UPDATE)
        
        self.main.refresh_time = calendar.timegm(time.gmtime())
        gobject.idle_add(self.gui.set_multi_button,
                         not self.main.status(ST_NETWORK_FAILED))
    
    
    # Update -------------------------------------------------------------------
    # --------------------------------------------------------------------------
    def update(self):
        
        # Tweets
        updates = []
        if not self.refresh_messages:
            try:
                updates = self.try_get_items(self.get_updates,
                                             self.html.last_id)
            
            # Something went wrong...
            except (IOError, TweepError), error:
                self.main.unset_status(ST_UPDATE)
                gobject.idle_add(self.html.render)
                gobject.idle_add(self.main.handle_error, error)
                self.main.refresh_time = calendar.timegm(time.gmtime())
                return False
            
            if len(updates) > 0:
                self.html.save_last_id(updates[0].id)
        
        # Messages
        messages = []
        if (self.message_counter > 1 or self.refresh_messages) \
           and not self.refresh_now:
            
            try:
                messages = self.try_get_items(self.get_messages,
                                              self.message.last_id)
            
            # Something went wrong...
            except (IOError, TweepError), error:
                self.main.unset_status(ST_UPDATE)
                gobject.idle_add(self.message.render)
                gobject.idle_add(self.main.handle_error, error)
                self.main.refresh_time = calendar.timegm(time.gmtime())
                return False
            
            if len(messages) > 0:
                self.message.save_last_id(messages[0].id)
            
            self.message_counter = 0
        
        elif not self.refresh_now:
            self.message_counter += 1
        
        self.main.unset_status(ST_NETWORK_FAILED)
        
        # Update Views
        def update_views(updates, messages):
            # Notifications this INSERTS the tweets/messages
            self.show_notifications(updates, messages)
            
            if len(updates) > 0:
                self.html.push_updates()
            
            else:
                self.html.render()
            
            if len(messages) > 0:
                self.message.push_updates()
            
            else:
                self.message.render()
            
            # Update GUI
            self.unwait()
            self.finish = True
        
        gobject.idle_add(update_views, updates, messages)
        return True
    
    
    # Retrieve Tweets / Messages -----------------------------------------------
    def try_get_items(self, method, since_id=0, max_id=None, max_count=200):
        count = 0
        while True:
            count += 1
            try:
                # Try to get the updates and then break
                return method(since_id = since_id, max_id = max_id,
                              max_count = max_count)
            
            # Timeouts
            except socket.timeout, error:
                if count == 2:
                    raise error
            
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
    
    
    # Notifications ------------------------------------------------------------
    # --------------------------------------------------------------------------
    def show_notifications(self, updates, messages):
        username = self.main.username.lower()
        
        # Messages
        notify_message_list = []
        message_ids = []
        for i in messages:
            img_file = self.get_image(i, True)
            if not i.id in message_ids:
                message_ids.append(i.id)
                if i.sender.screen_name.lower() != username:
                    notify_message_list.append([lang.notification_message % \
                                        i.sender.screen_name, i.text, img_file,
                                        'messages'])
            
            self.message.update_list.append((i, img_file))
        
        count = len(notify_message_list)
        if count > 0:
            notify_message_list.reverse()
            if count > 1:
                for i in range(0, count):
                    notify_message_list[i][0] = lang.notification_index \
                                                % (notify_message_list[i][0],
                                                   i + 1, count)
        
        # Tweets
        notify_tweet_list = []
        updates_ids = []
        for i in updates:
            img_file = self.get_image(i)
            if not i.id in updates_ids:
                updates_ids.append(i.id)
                if i.user.screen_name.lower() != username:
                    if hasattr(i, 'retweeted_status'):
                        name = 'RT %s' % i.retweeted_status.user.screen_name
                        text = i.retweeted_status.text
                    
                    else:
                        name = i.user.screen_name
                        text = i.text
                    
                    e = 'tweets'
                    if i.in_reply_to_screen_name is not None:
                        if i.in_reply_to_screen_name.lower() == username:
                            e = 'reply'
                    
                    notify_tweet_list.append([name, text, img_file, e])
            
            self.html.update_list.append((i, img_file))
        
        count = len(notify_tweet_list)
        if count > 0:
            notify_tweet_list.reverse()
            if count > 1:
                for i in range(0, count):
                    notify_tweet_list[i][0] = lang.notification_index \
                                              % (notify_tweet_list[i][0],
                                                 i + 1, count)
        
        
        # Show Notifications
        if self.settings.is_true('notify'):
            self.notifier.add(notify_message_list + notify_tweet_list)
    
    
    # Helpers ------------------------------------------------------------------
    # --------------------------------------------------------------------------
    def do_render(self, view, init, last):
        view.push_updates()
        view.load_state = HTML_LOADED
        
        if init: # Finish the login
            self.started = True
            gobject.idle_add(self.main.on_login)
            gobject.idle_add(self.gui.set_multi_button, True)
        
        if last: # Show login notification
            gobject.idle_add(self.main.show_start_notifications)
    
    # Calculate refresh interval based on rate limit information
    def update_limit(self):
        ratelimit = self.api.rate_limit_status()
        if ratelimit is None:
            self.main.refresh_timeout = 60
            return
        
        minutes = (ratelimit['reset_time_in_seconds'] \
                   - calendar.timegm(time.gmtime())) / 60
        
        limit = ratelimit['remaining_hits']
        if limit > 0:
            limit = limit / (2.0 + 2.0 / 2)
            self.main.refresh_timeout = int(minutes / limit * 60 * 1.10)
            if self.main.refresh_timeout < 45:
                self.main.refresh_timeout = 45
        
        # Check for ratelimit
        count = ratelimit['hourly_limit']
        if count < 350:
            if not self.main.status(ST_WARNING_RATE):
                self.main.set_status(ST_WARNING_RATE)
                gobject.idle_add(self.gui.warning_button.show,
                                 lang.warning_button_rate_limit,
                                 lang.warning_rate_limit % count)
        
        else:
            self.main.unset_status(ST_WARNING_RATE)
    
    def get_image(self, item, message=False):
        if message:
            url = item.sender.profile_image_url
            user_id = item.sender.id
            name = item.sender.screen_name
        
        else:
            if hasattr(item, 'retweeted_status'):
                url = item.retweeted_status.user.profile_image_url
                user_id = item.retweeted_status.user.id
                name = item.retweeted_status.user.screen_name
            
            else:
                url = item.user.profile_image_url
                user_id = item.user.id
                name = item.user.screen_name
        
        image = url[url.rfind('/') + 1:]
        img_dir = os.path.join(HOME_DIR, '.atarashii')
        if not os.path.exists(img_dir):
            os.mkdir(img_dir)
        
        img_file = os.path.join(img_dir, str(user_id) + '_' + image)
        if not os.path.exists(img_file):
            urllib.urlretrieve(url, img_file)
        
        # Check for user picture!
        if name.lower() == self.main.username.lower():
            self.main.set_user_picture(img_file)
        
        return img_file

