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

from language import LANG as lang
from constants import ST_WARNING_RATE, ST_UPDATE, \
                      ST_HISTORY, ST_LOGIN_COMPLETE

from constants import MODE_MESSAGES, MODE_TWEETS, HTML_UNSET_ID, \
                      UNSET_TIMEOUT, HTML_RESET, HTML_LOADING, HTML_LOADED

from utils import tweepy, TweepError, compare

class Updater(threading.Thread):
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
        
        self.path = os.path.expanduser('~')
    
    
    # Init the Updater ---------------------------------------------------------
    # --------------------------------------------------------------------------
    def init(self):
        self.gui = self.main.gui
        
        # Init Views
        self.html = self.gui.html
        self.message = self.gui.message
        
        # Reset
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
        self.html.init_id = self.main.get_latest_id()
        self.message.init_id = self.main.get_latest_message_id()
        
        # xAuth Login, yes the app stuff is here, were else should it go?
        # Why should anyone else use the Atarashii App for posting from HIS
        # client? :D
        auth = tweepy.OAuthHandler("PYuZHIEoIGnNNSJb7nIY0Q",
                                   "Fw91zqMpMECFMJkdM3SFM7guFBGiFfkDRu0nDOc7tg",
                                   secure = True)
        
        try:
            # Try using an old token
            token_ok = False
            key_name = 'xkey_' + self.main.username
            secret_name = 'xsecret_' + self.main.username
            if self.settings.isset(key_name) and \
               self.settings.isset(secret_name):
                auth.set_access_token(self.settings[key_name],
                                      self.settings[secret_name])
                
                try:
                    auth.get_username()
                    token_ok = True
                
                except IOError, error:
                    raise error
                
                except TweepError, error:
                    self.settings[key_name] = ""
                    self.settings[secret_name] = ""
            
            # Get a new token!
            if not token_ok:
                gobject.idle_add(self.gui.force_show)
                gobject.idle_add(self.gui.enter_password)
                
                # Wait for password entry
                while self.main.api_temp_password == None:
                    time.sleep(0.1)
                
                # Try to login with the new password
                if self.main.api_temp_password != "":
                    token = auth.get_xauth_access_token(self.main.username,
                                                    self.main.api_temp_password)
                    
                    self.main.api_temp_password = None
                    self.settings[key_name] = token.key
                    self.settings[secret_name] = token.secret
                
                else:
                    gobject.idle_add(self.main.on_login_failed)
                    self.main.api_temp_password = None
                    return
        
        except (IOError, TweepError), error:
            self.main.api_temp_password = None
            gobject.idle_add(self.main.on_network_failed, error)
            return False
        
        # Create the api instance
        self.api = self.main.api = tweepy.API(auth)
        
        # Set loading to pending
        self.message.load_state = HTML_LOADING
        self.html.load_state = HTML_LOADING
        
        # Lazy loading
        if self.gui.mode == MODE_MESSAGES:
            if not self.get_init_messages():
                self.message.load_state = HTML_RESET
                self.html.load_state = HTML_RESET
                return
        
        elif self.gui.mode == MODE_TWEETS:
            if not self.get_init_tweets():
                self.message.load_state = HTML_RESET
                self.html.load_state = HTML_RESET
                return
        
        else: # TODO implement loading of search
            pass
        
        # Init the GUI
        self.started = True
        gobject.idle_add(self.main.on_login)
        gobject.idle_add(self.gui.check_read)
        
        # Load other stuff
        if self.gui.mode == MODE_TWEETS:
            if self.get_init_messages(True):
                if self.gui.mode == MODE_MESSAGES:
                    gobject.idle_add(self.gui.show_input)
                
                else:
                    gobject.idle_add(self.gui.check_refresh)
            
            else:
                self.message.load_state = HTML_RESET
                self.html.load_state = HTML_RESET
                return
        
        elif self.gui.mode == MODE_MESSAGES:
            if self.get_init_tweets(True):
                if self.gui.mode == MODE_TWEETS:
                    gobject.idle_add(self.gui.show_input)
                
                else:
                    gobject.idle_add(self.gui.check_refresh)
            
            else:
                self.message.load_state = HTML_RESET
                self.html.load_state = HTML_RESET
                return 
        
        else: # TODO implement loading of search
            pass
        
        # Force Title Update
        self.main.set_status(ST_LOGIN_COMPLETE)
        gobject.idle_add(self.gui.set_app_title)
        
        # Init Timer
        self.main.refresh_time = calendar.timegm(time.gmtime())
        gobject.idle_add(self.gui.check_read)
    
    
    # Load initial tweets ------------------------------------------------------
    def get_init_tweets(self, last = False):
        updates = []
        try:
            updates = self.try_get_updates(self.main.get_first_id())
        
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
                    
            # Show login message
            if last:
                self.gui.show_start_notifications()
        
        gobject.idle_add(render)
        return True
    
    
    # Load initial messages ----------------------------------------------------
    def get_init_messages(self, last = False):
        messages = []
        try:
            messages = self.try_get_messages(self.main.get_first_message_id())
        
        except (IOError, TweepError), error:
            gobject.idle_add(self.main.on_login_failed, error)
            return False
        
        if len(messages) > 0:
            self.set_last_message(messages[0].id)
        
        messages.reverse()
        for i in messages:
            if i != None:
                imgfile = self.get_image(i, True)
                self.message.update_list.append((i, imgfile))
        
        
        def render():
            self.message.push_updates()
            self.message.load_state = HTML_LOADED
                    
            # Show login message
            if last:
                self.gui.show_start_notifications()
        
        gobject.idle_add(render)
        return True
    
    
    # Mainloop -----------------------------------------------------------------
    # --------------------------------------------------------------------------
    def run(self):
        while self.running:
            if self.do_init:
                self.init()
            
            elif self.started:
                if self.html.load_history_id != HTML_UNSET_ID:
                    self.load_history()
                
                elif self.message.load_history_id != HTML_UNSET_ID:
                    self.load_history_message()
                
                elif self.main.refresh_timeout != UNSET_TIMEOUT:
                    self.check_for_update()
            
            time.sleep(0.1)
    
    
    # Update -------------------------------------------------------------------
    # --------------------------------------------------------------------------
    def check_for_update(self):
        if self.main.refresh_time == UNSET_TIMEOUT:
            return
        
        if calendar.timegm(time.gmtime()) > self.main.refresh_time + \
           self.main.refresh_timeout or self.refresh_now or \
           self.refresh_messages:
            
            self.main.set_status(ST_UPDATE)
            self.update()
            
            # Update crashfile
            self.main.settings.crash_file(True)
            
            # Update GUI
            gobject.idle_add(self.gui.refresh_button.set_sensitive, True)
            gobject.idle_add(self.gui.tray.refresh_menu.set_sensitive, True)
            
            gobject.idle_add(self.gui.check_read)
            self.main.refresh_time = calendar.timegm(time.gmtime())
            self.refresh_messages = False
            self.refresh_now = False
            self.main.unset_status(ST_UPDATE)
            gobject.idle_add(self.gui.update_status, True)
    
    def update(self):
        # Fetch Tweets
        updates = []
        if not self.refresh_messages:
            try:
                updates = self.try_get_updates(self.html.last_id)
            
            # Something went wrong...
            except (IOError, TweepError), error:
                gobject.idle_add(self.html.render)
                gobject.idle_add(self.gui.show_error, error)
                self.main.refresh_timeout = 60
                self.main.refresh_time = calendar.timegm(time.gmtime())
                return
            
            if len(updates) > 0:
                self.set_last_tweet(updates[0].id)
        
        # Messages
        messages = []
        if (self.message_counter > 1 or self.refresh_messages) and \
            not self.refresh_now:
            
            try:
                messages = self.try_get_messages(self.message.last_id)
            
            # Something went wrong...
            except (IOError, TweepError), error:
                gobject.idle_add(self.message.render)
                gobject.idle_add(self.gui.show_error, error)
                return
            
            if len(messages) > 0:
                self.set_last_message(messages[0].id)
            
            self.message_counter = 0
        
        elif not self.refresh_now:
            self.message_counter += 1
        
        # Disable read button before pushing updates into the trees
        self.gui.read_button.set_sensitive(False)
        
        # Notify
        self.show_notifications(updates, messages)
        
        # Update View
        if len(updates) > 0:
            gobject.idle_add(self.html.push_updates)
        
        else:
            gobject.idle_add(self.html.render)
        
        if len(messages) > 0:
            gobject.idle_add(self.message.push_updates)
        
        else:
            gobject.idle_add(self.message.render)
    
    
    # Notifications ------------------------------------------------------------
    # --------------------------------------------------------------------------
    def show_notifications(self, updates, messages):
        tweet_list = []
        tweet_ids = []
        message_ids = []
        for i in messages:
            imgfile = self.get_image(i, True)
            if i.sender.screen_name.lower() != self.main.username.lower():
                if not i.id in message_ids:
                    message_ids.append(i.id)
                    tweet_list.append([
                        lang.notification_message % i.sender.screen_name,
                        i.text, imgfile])
            
            self.message.update_list.append((i, imgfile))
        
        for i in updates:
            imgfile = self.get_image(i)
            if i.user.screen_name.lower() != self.main.username.lower():
                # Don't add mentions twice
                if not i.id in tweet_ids:
                    tweet_ids.append(i.id)
                    if hasattr(i, "retweeted_status"):
                        name = "RT %s" % i.retweeted_status.user.screen_name
                        text = i.retweeted_status.text
                    else:
                        name = i.user.screen_name
                        text = i.text
                    
                    tweet_list.append([name, text, imgfile])
            
            self.html.update_list.append((i, imgfile))
        
        # Show Notifications
        count = len(tweet_list)
        if count > 0 and self.settings.is_true("notify"):
            tweet_list.reverse()
            if count > 1:
                for num, i in enumerate(tweet_list):
                    tweet_list[num][0] = lang.notification_index % (
                                        tweet_list[num][0], num+1, count)
            
            self.notifier.show(tweet_list)
    
    
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
                updates = self.api.home_timeline(max_id = max_id,
                                                 count = max_count)
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
            gobject.idle_add(self.gui.show_error, error)
            return False
        
        self.main.max_tweet_count += len(updates)
        for i in updates:
            imgfile = self.get_image(i)
            self.html.history_list.append((i, imgfile))
        
        self.html.load_history_id = HTML_UNSET_ID
        self.main.unset_status(ST_HISTORY)
        
        if len(updates) > 0:
            self.html.load_history = True
            self.html.history_loaded = True
            self.html.history_count += len(updates)
            self.gui.history_button.set_sensitive(True)
        
        gobject.idle_add(self.html.push_updates)
        gobject.idle_add(self.gui.show_input)
    
    
    # Main Function that fetches the messages ----------------------------------
    # --------------------------------------------------------------------------
    def try_get_messages(self, since_id = 0, max_id = None, max_count = 200):
        count = 0
        while True:
            count += 1
            try:
                # Try to get the updates and then break
                return self.get_messages(since_id = since_id, max_id = max_id,
                                max_count = max_count)
            
            # Stop immediately on network error
            except IOError, error:
                raise error
            
            # Something went wrong, either try it again or break with the error
            except TweepError, error:
                if count == 2:
                    raise error
    
    # Messages
    def get_messages(self, since_id = 0, max_id = None, max_count = 200):
        messages = []
        if since_id != HTML_UNSET_ID:
            if max_id == None:
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
        return self.process_updates(messages)
    
    # Message History
    def load_history_message(self):
        messages = []
        try:
            messages = self.try_get_messages(
                            max_id = self.message.load_history_id,
                            max_count = self.main.load_message_count)
        
        except (IOError, TweepError), error:
            self.message.load_history_id = HTML_UNSET_ID
            self.main.unset_status(ST_HISTORY)
            gobject.idle_add(self.gui.show_error, error)
            return False
        
        self.main.max_message_count += len(messages)
        for i in messages:
            imgfile = self.get_image(i, True)
            self.message.history_list.append((i, imgfile))
        
        self.message.load_history_id = HTML_UNSET_ID
        self.main.unset_status(ST_HISTORY)
        
        if len(messages) > 0:
            self.message.load_history = True
            self.message.history_loaded = True
            self.message.history_count += len(messages)
            self.gui.history_button.set_sensitive(True)
        
        gobject.idle_add(self.message.push_updates)
        gobject.idle_add(self.gui.show_input)
    
    
    # Helpers ------------------------------------------------------------------
    # --------------------------------------------------------------------------
    def set_last_tweet(self, item_id):
        self.html.last_id = item_id
        self.settings['lasttweet_' + self.main.username] = item_id
        if len(self.html.items) > 0:
            self.html.newest_id = self.html.items[
                                            len(self.html.items) - 1][0].id
    
    def set_last_message(self, item_id):
        self.message.last_id = item_id
        self.settings['lastmessage_' + self.main.username] = item_id
        if len(self.message.items) > 0:
            self.message.newest_id = self.message.items[
                                          len(self.message.items) - 1][0].id
    
    def process_updates(self, updates):
        # Remove doubled mentions
        ids = []
        def unique(i):
            # Check if this item is already in the list
            if i.id in ids:
                return False
            
            else:
                ids.append(i.id)
                return True
        
        updates = filter(unique, updates)
        updates.sort(compare)
        return updates
    
    def update_limit(self):
        ratelimit = self.api.rate_limit_status()
        if ratelimit == None:
            self.main.refresh_timeout = 60
            return
        
        minutes = (ratelimit['reset_time_in_seconds'] - \
                   calendar.timegm(time.gmtime())) / 60
        
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
    
    def get_image(self, item, message = False):
        if message:
            url = item.sender.profile_image_url
            userid = item.sender.id
            name = item.sender.screen_name
        
        else:
            if hasattr(item, "retweeted_status"):
                url = item.retweeted_status.user.profile_image_url
                userid = item.retweeted_status.user.id
                name = item.retweeted_status.user.screen_name
            
            else:
                url = item.user.profile_image_url
                userid = item.user.id
                name = item.user.screen_name
        
        image = url[url.rfind('/') + 1:]
        imgdir = os.path.join(self.path, ".atarashii")
        if not os.path.exists(imgdir):
            os.mkdir(imgdir)
        
        imgfile = os.path.join(imgdir, str(userid) + '_' + image)
        if not os.path.exists(imgfile):
            urllib.urlretrieve(url, imgfile)
        
        # Check for user picture!
        if name.lower() == self.main.username.lower():
            self.main.set_user_picture(imgfile)        
        
        return imgfile

