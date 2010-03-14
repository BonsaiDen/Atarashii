# -*- coding: UTF-8 -*-

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


# Translations -----------------------------------------------------------------
# ------------------------------------------------------------------------------
import locale
LANG = {
    
    # German -------------------------------------------------------------------
    # --------------------------------------------------------------------------
    'de_DE' : {
        
        # Title
        'title' : 'Atarashii',
        'title_logged_in' : '%s - Atarashii',
        'title_message' : '%d neue Nachricht',
        'title_messages' : '%d neue Nachrichten',
        'title_tweet' : '%d neuer Tweet',
        'title_tweets' : '%d neue Tweets',
        
        # HTML
        'html_welcome' : 'Willkommen bei Atarashii!',
        'html_loading' : 'Tweets werden geladen...',
        'html_info' : 'Name: %s\nFollower: %d\nFollowing: %d\nTweets: %d',
        'html_profile' : '%s auf Twitter.com',
        'html_at' : '%s auf Twitter.com',
        'html_reply' : '%s antworten',
        'html_retweet' : '%s retweeten',
        'html_time' : 'Getwittert um %H:%M:%S Uhr',
        'html_time_day' : 'Getwittert am %d.%m.%Y um %H:%M:%S Uhr',
        'html_search' : 'Suche nach &quot;%s&quot;',
        'html_by' : ' von %s',
        'html_in_reply' : 'in Antwort auf %s',
        'html_in_retweet' : 'retweeted von %s',
        'html_load_more' : 'Mehr',
        'html_empty' : 'Keine Tweets',
        'html_protected' : '%s\'s Tweets sind geschützt',
        'html_about_second' : 'vor circa einer Sekunde',
        'html_second' : 'vor %d Sekunden',
        'html_about_minute' : 'vor circa einer Minute',
        'html_minute' : 'vor %d Minuten',
        'html_about_hour' : 'vor circa einer Stunde',
        'html_hour' : 'vor %d Stunden',
        'html_about_day' : 'vor circa einem Tag',
        'html_day' : 'vor %d Tagen',
        'html_yesterday' : 'von Gestern',
        'html_exact' : 'vom %d.%m.%Y',
        
        # Messages
        'message_loading' : 'Nachrichten werden geladen...',
        'message_load_more' : 'Mehr',
        'message_empty' : 'Keine Nachrichten',
        'message_from' : 'Von',
        'message_to' : 'An',
        
        # Notifications
        'notification_message' : 'Nachricht von %s',
        'notification_index' : '%s (%d von %d)',
        
        # Textbox
        'text_entry' : 'Was passiert gerade?',
        'text_entry_message' : 'Nachricht eingeben...',
        
        # Statusbar
        'status_logout' : 'Nicht verbunden.',
        'status_connecting' : 'Verbinde als %s...',
        'status_connected' : 'Verbunden, aktualisiere...',
        'status_error' : 'Verbindung fehlgeschlagen.',
        'status_seconds' : 'Aktualisierung in %s Sekunden.',
        'status_one_second' : 'Aktualisierung in einer Sekunde.',
        'status_minute' : 'Aktualisierung in einer Minute.',
        'status_minutes' : 'Aktualisierung in %d Minuten.',
        'status_update' : 'Aktualisiere...',
        'status_reply' : 'Antworte %s...',
        'status_retweet' : 'Retweete %s...',
        'status_message' : 'Sende Nachricht an %s...',
        'status_message_reply' : 'Antworte %s...',
        'status_send' : 'Sende Status...',
        'status_left' : 'Noch %d Zeichen.',
        'status_more' : '%d Zeichen zu viel.',
        'status_load_history' : 'Tweets werden geladen...',
        'status_load_message_history' : 'Nachrichten werden geladen...',
        'status_reconnect_seconds' : 'Automatischer Reconnect in %d Sekunden.',
        'status_reconnect_minute' : 'Automatischer Reconnect in einer Minute.',
        'status_reconnect_minutes' : 'Automatischer Reconnect in %d Minuten.',
        
        # Info Label
        'label_reply' : '<b>Antwort an %s:</b>',
        'label_reply_text' : '<b>Antwort auf:</b> %s',
        'label_retweet' : '<b>%s retweeten:</b>',
        'label_message' : '<b>Nachricht an %s:</b>',
        'label_message_text' : '<b>Antwort auf:</b> %s',
        
        # Settings Dialog
        'settings_title' : 'Atarashii - Einstellungen',
        'settings_button' : 'Speichern',
        'settings_buttonCancel' : 'Abbrechen',
        'settings_accounts' : 'Benutzer',
        'settings_notifications' : 'Benachrichtigungen',
        'settings_notify' : 'Aktivieren',
        'settings_sound' : 'Sound abspielen',
        'settings_file' : 'Sounddatei',
        'settings_file_filter' : 'Soundateien',
        'settings_retweets' : 'Retweets',
        'settings_retweets_ask' : 'Immer fragen',
        'settings_retweets_new' : 'Immer neue Retweets verwenden',
        'settings_retweets_old' : 'Immer alte Retweets verwenden',
        'settings_add' : 'Erstellen',
        'settings_edit' : 'Bearbeiten',
        'settings_delete' : 'Löschen',
        
        # About Dialog
        'about_title' : 'Über Atarashii',
        'about_license_button' : 'Lizenz',
        'about_okbutton' : 'OK',
        
        # Account Dialog
        'account_edit' : 'Benutzer bearbeiten',
        'account_create' : 'Benutzer erstellen',
        'account_delete' : 'Benutzer löschen',
        'account_delete_description' : 'Möchten sie den Benutzer "%s" wirklich löschen?',
        'account_button' : 'OK',
        'account_button_cancel' : 'Abbrechen',
        'account_username' : 'Benutzername:',
        
        # Password Dialog
        'password_button' : 'OK',
        'password_button_cancel' : 'Abbrechen',
        'password_title' : 'Passwort',
        'password_question' : '%s\'s Passwort:',
        
        # Retweet Dialogs
        'retweet_title' : '%s retweeten',
        'retweet_question' : 'Möchten sie einen neuen Retweet verwenden?',
        'retweet_info_title' : 'Retweet erfolgreich',
        'retweet_info' : '"%s" wurde erfolgreich retweeted!',
        
        # Error Dialogs
        'error_title' : 'Atarashii - Fehler',
        'error_login' : 'Die Anmeldung als "%s" ist fehlgeschlagen.',
        'error_ratelimit' : 'Ratelimit erreicht. Automatische Aktualisierung in %d Minute(n).',
        'error_ratelimit_reconnect' : 'Ratelimit erreicht. Automatischer Reconnect in %d Minute(n).',
        'error_twitter' : 'Interner Twitterfehler.',
        'error_down' : 'Twitter ist gerade offline.',
        'error_overload' : 'Twitter ist gerade überlastet.',
        'error_internal' : 'Atarashii Fehler: %s',
        'error_already_retweeted' : 'Es ist entweder nicht möglich diesen Tweet zu retweeten oder er wurde bereits von ihnen retweeted.',
        'error_user_not_found' : 'Der Benutzer "%s" existiert nicht.',
        
        # Warning Dialogs
        'warning_title' : 'Atarashii - Warnung',
        'warning_text' : 'Twitter hat das Ratelimit auf %d Requests pro Stunde reduziert, das Updateinterval wurde entsprechend angepasst.',
        'warning_url' : 'Atarashii konnte Twitter nicht erreichen, dies ist in den meisten Fällen lediglich ein temporäres Problem aufgrund von Überlastung seitens Twitter.',
        
        # Toolbar Items
        'tool_refresh' : 'Tweets aktualisieren',
        'tool_history' : 'Ältere Tweets entfernen',
        'tool_read' : 'Alle Tweets als gelesen markieren',
        'tool_mode' : 'Nachrichten',
        'tool_settings' : 'Einstellungen öffnen',
        'tool_about' : 'Einige Informationen über Atarashii',
        'tool_quit' : 'Atarashii beenden',
        'tool_refresh_message' : 'Nachrichten aktualisieren',
        'tool_history_message' : 'Ältere Nachrichten entfernen',
        'tool_read_message' : 'Alle Nachrichten als gelesen markieren',
        
        # Tray Menu
        'menu_update' : 'Aktualisieren',
        'menu_settings' : 'Einstellungen',
        'menu_about' : 'Über Atarashii',
        'menu_quit' : 'Beenden'
    },
    
    # English ------------------------------------------------------------------
    # --------------------------------------------------------------------------
    'en_US' : {
        
        # Title
        'title' : 'Atarashii',
        'title_logged_in' : '%s - Atarashii',
        'title_message' : '%d new Message',
        'title_messages' : '%d new Messages',
        'title_tweet' : '%d new Tweet',
        'title_tweets' : '%d new Tweets',
        
        # HTML
        'html_welcome' : 'Welcome to Atarashii!',
        'html_loading' : 'Loading Tweets...',
        'html_info' : 'Name: %s\nFollower: %d\nFollowing: %d\nTweets: %d',
        'html_profile' : '%s at Twitter.com',
        'html_at' : '%s at Twitter.com',
        'html_reply' : 'Reply to %s',
        'html_retweet' : 'Retweet %s',
        'html_time' : 'Tweeted at %H:%M:%S',
        'html_time_day' : 'Tweeted on %m.%d.%Y at %H:%M:%S',
        'html_search' : 'Search for &quot;%s&quot;',
        'html_by' : ' by %s',
        'html_in_reply' : 'in reply to %s',
        'html_in_retweet' : 'retweeted by %s',
        'html_load_more' : 'More',
        'html_empty' : 'No Tweets',
        'html_protected' : '%s\'s Tweets are protected',
        'html_about_second' : 'about one second ago',
        'html_second' : '%d seconds ago',
        'html_about_minute' : 'about a minute ago',
        'html_minute' : '%d minutes ago',
        'html_about_hour' : 'about an hour ago',
        'html_hour' : '%d hours ago',
        'html_about_day' : 'about a day ago',
        'html_day' : '%d days ago',
        'html_yesterday' : 'from yesterday',
        'html_exact' : 'from %m.%d.%Y',
        
        # Messages
        'message_loading' : 'Loading messages...',
        'message_load_more' : 'More',
        'message_empty' : 'No Messages',
        'message_from' : 'From',
        'message_to' : 'To',
        
        # Notifications
        'notification_message' : 'Message from %s',
        'notification_index' : '%s (%d of %d)',
        
        # Textbox
        'text_entry' : 'What\'s happening?',
        'text_entry_message' : 'Enter Message...',
        
        # Statusbar
        'status_logout' : 'Not connected.',
        'status_connecting' : 'Connecting as %s...',
        'status_connected' : 'Connected, loading...',
        'status_error' : 'Connection failed.',
        'status_seconds' : 'Refresh in %s seconds.',
        'status_one_second' : 'Refresh in one second.',
        'status_minute' : 'Refresh in one minute.',
        'status_minutes' : 'Refresh in %d minutes.',
        'status_update' : 'Sending Status...',
        'status_reply' : 'Replying to %s...',
        'status_retweet' : 'Retweeting %s...',
        'status_message' : 'Sending Message to %s...',
        'status_message_reply' : 'Replying to %s...',
        'status_send' : 'Sending Status...',
        'status_left' : '%d chars left.',
        'status_more' : '%d chars too much.',
        'status_load_history' : 'Loading Tweets...',
        'status_load_message_history' : 'Loading Messages...',
        'status_reconnect_seconds' : 'Automatic reconnect in %d seconds.',
        'status_reconnect_minute' : 'Automatic reconnect in one minute.',
        'status_reconnect_minutes' : 'Automatic reconnect in %d minutes.',
        
        # Info Label
        'label_reply' : '<b>Reply to %s:</b>',
        'label_reply_text' : '<b>Reply on:</b> %s',
        'label_retweet' : '<b>Retweet %s:</b>',
        'label_message' : '<b>Message to %s:</b>',
        'label_message_text' : '<b>Message on:</b> %s',
        
        # Settings Dialog
        'settings_title' : 'Atarashii - Preferences',
        'settings_button' : 'Save',
        'settings_buttonCancel' : 'Cancel',
        'settings_accounts' : 'Users',
        'settings_notifications' : 'Notifications',
        'settings_notify' : 'Enable',
        'settings_sound' : 'Play sound',
        'settings_file' : 'Soundfile',
        'settings_file_filter' : 'Soundfiles',
        'settings_retweets' : 'Retweets',
        'settings_retweets_ask' : 'Always ask which style to use',
        'settings_retweets_new' : 'Always use new style',
        'settings_retweets_old' : 'Always use old style',
        'settings_add' : 'Add',
        'settings_edit' : 'Edit',
        'settings_delete' : 'Delete',
        
        # About Dialog
        'about_title' : 'About Atarashii',
        'about_license_button' : 'License',
        'about_okbutton' : 'OK',
        
        # Account Dialog
        'account_edit' : 'Edit user',
        'account_create' : 'Create a new user',
        'account_delete' : 'Delete user',
        'account_delete_description' : 'Do you really want to delete the user "%s"?',
        'account_button' : 'OK',
        'account_button_cancel' : 'Cancel',
        'account_username' : 'Username:',
        'password_button' : 'OK',
        'password_button_cancel' : 'Cancel',
        'password_title' : 'Password',
        'password_question' : '%s\'s password:',
        
        # Retweet Dialogs
        'retweet_title' : 'Retweet %s',
        'retweet_question' : 'Do you want to use a new style Retweet?',
        'retweet_info_title' : 'Retweet successful',
        'retweet_info' : '"%s" has been successfully retweeted!',
        
        # Error Dialogs
        'error_title' : 'Atarashii - Error',
        'error_login' : 'The login as "%s" has failed.',
        'error_ratelimit' : 'Reached rate limit. Automatic refresh in %d minute(s).',
        'error_ratelimit_reconnect' : 'Reached rate limit. Automatic reconnect in %d minute(s).',
        'error_twitter' : 'Internal Twitter error.',
        'error_down' : 'Twitter is currently offline.',
        'error_overload' : 'Twitter is over capacity.',
        'error_internal' : 'Atarashii error: %s',
        'error_already_retweeted' : 'Either it\'s not possible to retweet this Tweet or you\'ve already retweeted it.',
        'error_user_not_found' : 'The user "%s" does not exist.',
        
        # Warning Dialogs
        'warning_title' : 'Atarashii - Warning',
        'warning_text' : 'Twitter has lowered the rate limit to %d requests per hour, the update interval has been adjusted accordingly.',
        'warning_url' : 'Atarashii couldn\'t connect to Twitter, in most cases this is just a temporary issue due to Twitter being too busy at the moment.',
        
        # Toolbar items
        'tool_refresh' : 'Refresh Tweets',
        'tool_history' : 'Remove History',
        'tool_read' : 'Mark all Tweets as read',
        'tool_mode' : 'Messages',
        'tool_settings' : 'Open Preferences',
        'tool_about' : 'Some information about Atarashii',
        'tool_quit' : 'Quit Atarashii',
        'tool_refresh_message' : 'Refresh Message',
        'tool_history_message' : 'Remove History',
        'tool_read_message' : 'Mark all Messages as read',
        
        # Tray Menu
        'menu_update' : 'Refresh',
        'menu_settings' : 'Preferences',
        'menu_about' : 'About Atarashii',
        'menu_quit' : 'Quit'
    }
}


class Language:
    def __init__(self, code):
        if LANG.has_key(code):
            stuff = LANG[code]
        
        else:
            stuff = LANG['en_US']
        
        # set instance fields
        for k, v in stuff.iteritems():
            self.__dict__[k] = v

# Select Language
lang = Language(locale.getdefaultlocale()[0])

