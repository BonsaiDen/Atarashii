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
        
        # Username
        'name' : lambda x: x + '\'' if x[-1:] in 'xs' else x + 's',

        # HTML
        'html_welcome' : 'Willkommen bei Atarashii.',
        'html_loading' : 'Tweets werden geladen...',
        'html_avatar_tooltip' :
            '<span size="large"><b>%s</b></span>\n<b>%d</b> Tweets\n'
            '<b>%d</b> Follower\nFollowing <b>%d</b>',
        
        'html_expanded_tooltip' : '<b>%s</b> verweist auf:\n%s',
        
        'html_profile' : '%s auf Twitter.com',
        'html_at' : '%s auf Twitter.com',
        'html_reply' : '%s antworten',
        'html_retweet' : '%s retweeten',
        'html_favorite' : 'Favorisieren!',
        'html_unfavorite' : 'Normalisieren',
        'html_time' : 'Getwittert um %H:%M:%S Uhr',
        'html_time_day' : 'Getwittert am %d.%m.%Y um %H:%M:%S Uhr',
        'html_search' : 'Suche nach &quot;%s&quot;',
        'html_by' : ' von %s',
        'html_in_reply' : 'in Antwort auf %s',
        'html_in_retweet' : 'retweeted von %s',
        'html_load_more' : 'Mehr',
        'html_empty' : 'Keine Tweets',
        'html_protected' : '%s Tweets sind geschützt',
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
        'notification_index' : '%s (%d von %d)', # "Message (3 of 4)"
        'notification_login' : '%s wurde angemeldet',
        'notification_login_tweet' : '%d neuer Tweet',
        'notification_login_message' : '%d neue Nachricht',
        'notification_login_tweets' : '%d neue Tweets',
        'notification_login_messages' : '%d neue Nachrichten',
        
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
        'status_deleting_tweet' : 'Lösche Tweet...',
        'status_deleting_message' : 'Lösche Nachricht...',
        'status_edit' : 'Bearbeite Tweet...',
        'status_edit_reply' : 'Bearbeite Antwort an %s...',
        
        # Info Label
        'label_reply' : '<b>Tweet an %s:</b>',
        'label_reply_text' : '<b>Antwort auf:</b> %s',
        'label_retweet' : '<b>%s retweeten:</b>',
        'label_message' : '<b>Nachricht an %s:</b>',
        'label_message_text' : '<b>Antwort auf:</b> %s',
        'label_edit' : '<b>Tweet bearbeiten:</b> %s',
        'label_edit_reply' : '<b>Antwort an %s bearbeiten:</b> %s',
        
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
        'settings_general' : 'Allgemein',
        'settings_autostart' : 'Atarashii beim Login starten',
        'settings_tray' : 'Minimiert starten(System Tray)',
        'settings_taskbar' : 'Atarashii in der Taskleiste anzeigen',
        'settings_shortener' : 'URL-Kürzer:',
        'settings_add' : 'Erstellen',
        'settings_edit' : 'Bearbeiten',
        'settings_delete' : 'Löschen',
        'settings_file_ok' : 'OK',
        'settings_file_cancel' : 'Abbrechen',
        
        # About Dialog
        'about_title' : 'Über Atarashii',
        'about_license_button' : 'Lizenz',
        'about_okbutton' : 'OK',
        'about_description' :
            'Ein simpler Twitter Client für den GNOME Desktop.',
            
        'about_kittens' : 
            'Diese Version wurde von <b>%s</b> Kätzchen\n'
            'verpackt. Ihre Glückszahl ist <b>%s</b>!',
        
        # Account Dialog
        'account_edit' : 'Benutzer bearbeiten',
        'account_create' : 'Benutzer erstellen',
        'account_delete' : 'Benutzer löschen',
        'account_delete_description' :
        'Möchten sie den Benutzer <b>%s</b> wirklich löschen?',
        
        'account_button' : 'OK',
        'account_button_cancel' : 'Abbrechen',
        'account_username' : 'Benutzername:',
        
        # Password Dialog
        'password_button' : 'OK',
        'password_button_cancel' : 'Abbrechen',
        'password_title' : 'Passwort',
        'password_question' : '<b>%s</b> Passwort:',
        'password_too_short' : '<i><b>Fehler:</b> Mindestens 6 Zeichen.</i>',
        
        # Retweet Dialogs
        'retweet_info_title' : 'Retweet erfolgreich',
        'retweet_info' : '<b>%s</b> wurde erfolgreich retweeted.',
        
        # Delete Dialogs
        'delete_title' : 'Löschen bestätigen',
        'delete_tweet_question' :
        '<b>Diesen Tweet wirklich löschen?</b>\n<i>%s</i>',
        
        'delete_message_question' :
        '<b>Diese Nachricht wirklich löschen?</b>\n<i>%s</i>',
        
        'delete_info_title' : 'Löschen erfolgreich',
        'delete_info_tweet' : 'Der Tweet wurde erfolgreich gelöscht.',
        'delete_info_message' : 'Die Nachricht wurde erfolgreich gelöscht.',
        
        
        # Crash Error Dialogs
        'error_general' : 
            '<span size="large"><b>Atarashii ist abgestürzt...</b></span>\n'
            '...hat sich aber automatisch neu gestartet!\n\n'
            'Im Normalfall sollten keine Daten verloren gegangen sein.\n\n',
        
        'error_crashed_title' : 'Keizoku wa chikara nari',
        'error_crashed' : 
            'Es handelt sich um einen <b>externen</b> Fehler mit dem Code '
            '<b>%s</b>, mehr konnten die Kätzchen leider nicht herausfinden.',
        
        'error_crashed__python_title' : 'Snake? Snake? Snaaaaaaaaaaake!',
        'error_crashed_python' : 
            'Es handelt sich um einen <b>internen</b> Fehler das Log finden '
            'sie <a href="file://%s">hier</a>.',
        
        # User Errors
        'error_title' : 'Atarashii - Fehler',
        'error_login' :
            'Die Anmeldung als <b>%s</b> ist fehlgeschlagen.',
        
        'error_already_retweeted' :
            'Es ist entweder nicht möglich diesen Tweet zu retweeten '
            'oder er wurde bereits von ihnen retweeted.',
        
        'error_user_not_found' : 'Der Benutzer <b>%s</b> existiert nicht.',
        'error_duplicate' : 'Sie haben dies bereits getweetet.',
        'error_tweet_not_found' : 'Dieser Tweet wurde bereits gelöscht.',
        'error_message_not_found' : 'Diese Nachricht wurde bereits gelöscht.',
        
        
        'error_network' :
            'Atarashii konnte keine Verbindung zum Internet herstellen.',
        
        'error_network_timeout' :
            'Atarashii konnte keine Verbindung zu Twitter herstellen.',
        
        'error_favorite_on' :
            '<b>%s</b> Tweet konnte nicht favorisiert werden.',
        
        'error_favorite_off' :
            '<b>%s</b> Tweet konnte nicht entfavorisiert werden.',
        
        'error_ratelimit_reconnect' :
            'Twitter Requestlimit wurde überschritten.\n'
            'Verbinde automatisch neu in %d Minute(n).',
        
        # Error Button stuff
        'error_button_twitter' : 'Twitter Serverfehler',
        'error_twitter' :
            'Der Twitter Server hat keine Antwort gesendet.',
        
        'error_button_down' : 'Twitter ist derzeit offline',
        'error_down' : 'Twitter konnte nicht erreicht werden.',
        
        'error_button_rate_limit' : 'Requestlimit überschritten',
        'error_rate_limit' :
            'Twitter Requestlimit wurde überschritten.\n'
            'Automatische Aktualisierung in %d Minute(n).',
        
        'error_template' : '<b>Fehler von %H:%M:%S Uhr</b>\n',
        
        # Warning Dialogs
        'warning_title' : 'Atarashii - Warnung',
        
        'warning_button_rate_limit' : 'Requestlimit verringert',
        'warning_rate_limit' :
            'Twitter hat das Requestlimit auf %d Requests pro Stunde '
            'reduziert, das Aktualisierungsinterval wurde '
            'entsprechend angepasst.',
        
        'warning_button_overload' : 'Twitter überlastet',
        'warning_overload' :
            'Atarashii konnte Twitter nicht erreichen, dies ist in '
            'den meisten Fällen lediglich ein temporäres Problem '
            'aufgrund von Überlastung seitens Twitter.',
        
        'warning_button_network' : 'Netzwerkfehler',
        'warning_network' :
            'Atarashii hat die Verbindung zum <b>Internet</b> verloren,'
            ' es wird alle 60 Sekunden versucht die Verbindung '
            'wiederherzustellen.',
        
        'warning_network_timeout' :
            'Atarashii hat die Verbindung zu <b>Twitter</b> verloren, '
            'es wird alle 60 Sekunden versucht die Verbindung '
            'wiederherzustellen.',
        
        'warning_template' : '<b>Warnung von %H:%M:%S Uhr</b>\n',
        
        # Buttons
        'button_open' : 'Für weitere Informationen klicken',
        
        # Toolbar Items
        'tool_refresh' : 'Tweets aktualisieren',
        'tool_history' : 'Ältere Tweets zurücksetzen',
        'tool_read' : 'Alle Tweets als gelesen markieren',
        'tool_mode' : 'Nachrichten',
        'tool_settings' : 'Einstellungen öffnen',
        'tool_about' : 'Über Atarashii',
        'tool_quit' : 'Atarashii beenden',
        'tool_refresh_message' : 'Nachrichten aktualisieren',
        'tool_history_message' : 'Ältere Nachrichten entfernen',
        'tool_read_message' : 'Alle Nachrichten als gelesen markieren',
        
        # Tray Menu
        'menu_update' : 'Aktualisieren',
        'menu_read' : 'Alle als gelesen markieren',
        'menu_settings' : 'Einstellungen',
        'menu_about' : 'Über Atarashii',
        'menu_quit' : 'Beenden',
        
        # Tray Tooltip
        'tray_title' : 'Atarashii',
        'tray_logging_in' : 'Verbinde als <b>%s</b>...',
        'tray_logged_out' : 'Nicht verbunden.',
        'tray_logged_in' : 'Angemeldet als <b>%s</b>.',
        
        'tray_tweet' : '<b>%d</b> neuer Tweet',
        'tray_message' : '<b>%d</b> neue Nachricht',
        'tray_tweets' : '<b>%d</b> neue Tweets',
        'tray_messages' : '<b>%d</b> neue Nachrichten' ,
        
        # These are shown in the notifications, tags get removed
        'tray_error_login' : 'Anmeldung als <b>%s</b> fehlgeschlagen.',
        'tray_error_rate' : 'Requestlimit überschritten.',
        'tray_warning_network' : '<b>Netzwerkfehler.</b>',
        'tray_warning_twitter' : '<b>Twitter ist überlastet</b>',
        'tray_error_twitter' : 'Twitter Serverfehler.',
        'tray_error_down' : 'Twitter ist derzeit offline.',
        'tray_error_rate_limit' : 'Requestlimit überschritten.',
        
        # Context Menu
        'context_browser' : 'Im Browser öffnen',
        'context_copy' : 'Link kopieren',
        'context_copy_tweet' : 'Tweet kopieren',
        'context_copy_message' : 'Nachricht kopieren',
        'context_profile' : '%s auf Twitter.com',
        'context_reply' : '%s antworten...',
        'context_tweet' : 'Tweet an %s...',
        'context_message' : 'Nachricht an %s...',
        'context_source' : '%s Homepage',
        'context_view' : 'Auf Twitter.com aufrufen',
        'context_search' : 'Auf Twitter.com suchen',
        'context_retweet_old' : '%s via RT retweeten',
        'context_retweet_new' : '%s via Twitter retweeten',
        'context_delete_tweet' : 'Tweet löschen',
        'context_delete_message' : 'Nachricht löschen',
        'context_edit_tweet' : 'Tweet bearbeiten'
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
        
        # Username
        'name' : lambda x: x + '\'s' if x[-1:] in 'xs' else x + 's',
        
        # HTML
        'html_welcome' : 'Welcome to Atarashii.',
        'html_loading' : 'Loading Tweets...',
        'html_avatar_tooltip' :
            '<span size="large"><b>%s</b></span>\n<b>%d</b> Tweets\n'
            '<b>%d</b> Follower\nFollowing <b>%d</b>',
        
        'html_expanded_tooltip' : '<b>%s</b> redirects to:\n%s',
        
        'html_profile' : '%s at Twitter.com',
        'html_at' : '%s at Twitter.com',
        'html_reply' : 'Reply to %s',
        'html_retweet' : 'Retweet %s',
        'html_favorite' : 'Favorite!',
        'html_unfavorite' : 'Normalize',
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
        'notification_login' : '%s has logged in',
        'notification_login_tweet' : '%d new Tweet',
        'notification_login_message' : '%d new Message',
        'notification_login_tweets' : '%d new Tweets',
        'notification_login_messages' : '%d new Messages',
        
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
        'status_deleting_tweet' : 'Deleting Tweet...',
        'status_deleting_message' : 'Deleting Message...',
        'status_edit' : 'Editing Tweet...',
        'status_edit_reply' : 'Editing Reply to %s...',
        
        # Info Label
        'label_reply' : '<b>Tweet to %s:</b>',
        'label_reply_text' : '<b>Reply on:</b> %s',
        'label_retweet' : '<b>Retweet %s:</b>',
        'label_message' : '<b>Message to %s:</b>',
        'label_message_text' : '<b>Message on:</b> %s',
        'label_edit' : '<b>Edit Tweet:</b> %s',
        'label_edit_reply' : '<b>Edit Reply to %s:</b> %s',
        
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
        'settings_general' : 'General',
        'settings_autostart' : 'Launch Atarashii on user login',
        'settings_tray' : 'Start minimized(system tray)',
        'settings_taskbar' : 'Show Atarashii in the Taskbar',
        'settings_shortener' : 'URL-Shortener:',
        'settings_add' : 'Add',
        'settings_edit' : 'Edit',
        'settings_delete' : 'Delete',
        'settings_file_ok' : 'OK',
        'settings_file_cancel' : 'Cancel',
        
        # About Dialog
        'about_title' : 'About Atarashii',
        'about_license_button' : 'License',
        'about_okbutton' : 'OK',
        'about_description' :
            'A simple Twitter Client for the GNOME Desktop.',
        
        'about_kittens' : 
            'This Version has been build by <b>%s</b> kittens.\n'
            'Their lucky number is <b>%s</b>!',
        
        # Account Dialog
        'account_edit' : 'Edit user',
        'account_create' : 'Create a new user',
        'account_delete' : 'Delete user',
        'account_delete_description' :
        'Do you really want to delete the user <b>%s</b>?',
        
        'account_button' : 'OK',
        'account_button_cancel' : 'Cancel',
        'account_username' : 'Username:',
        'password_button' : 'OK',
        'password_button_cancel' : 'Cancel',
        'password_title' : 'Password',
        'password_question' : '<b>%s</b> password:',
        'password_too_short' : '<i><b>Error:</b> At least 6 characters.</i>',
        
        # Retweet Dialogs
        'retweet_info_title' : 'Retweet successful',
        'retweet_info' : '<b>%s</b> has been successfully retweeted.',
        
        # Delete Dialogs
        'delete_title' : 'Confirm delete',
        'delete_tweet_question' :
        '<b>Are you sure to delete this Tweet?</b>\n<i>%s</i>',
        
        'delete_message_question' :
        '<b>Are you sure to delete this Message?</b>\n<i>%s</i>',
        
        'delete_info_title' : 'Deletion successful',
        'delete_info_tweet' : 'The Tweet has been successfully deleted.',
        'delete_info_message' : 'The Message has been successfully deleted.',
        
        # Crash Error Dialogs
        'error_general' : 
            '<span size="large"><b>Atarashii has crashed...</b></span>\n'
            '...but it has automatically restarted itself!\n\n'
            'In the normal case no data was lost.\n\n',
        
        'error_crashed_title' : 'Keizoku wa chikara nari',
        'error_crashed' : 
            'The error was an <b>external</b> one with the code <b>%s</b>,'
            ' that\'s all the Kittens could find out.',
        
        'error_crashed__python_title' : 'Snake? Snake? Snaaaaaaaaaaake!',
        'error_crashed_python' : 
            'The error was an <b>internal</b> one, you\'ll find the log '
            '<a href="file://%s">here</a>.',        
        
        # User Errors
        'error_title' : 'Atarashii - Error',
        'error_login' : 'The login as <b>%s</b> has failed.',
        'error_already_retweeted' :
            'Either it\'s not possible to retweet this Tweet or '
            'you\'ve already retweeted it.',
        
        'error_user_not_found' : 'The user <b>%s</b> does not exist.',
        'error_duplicate' : 'You\'ve already tweeted this.',
        'error_tweet_not_found' : 'This Tweet has already been deleted.',
        'error_message_not_found' : 'This Message has already been deleted.',
        
        'error_network' :
            'Atarashii could not establish a connection to the Internet.',
            
        'error_network_timeout' :
            'Atarashii could not establish a connection to Twitter.',
        
        'error_favorite_on' : '<b>%s</b> Tweet couldn\'t be favorited.',
        'error_favorite_off' : '<b>%s</b> Tweet couldn\'t be unfavorited.',
        
        'error_ratelimit_reconnect' :
             'Twitters limit on requests has been exceeded.\n'
             'Automatic reconnect in %d minute(s).',
        
        # Error Button stuff
        'error_button_twitter' : 'Twitter server error',
        'error_twitter' : 'The Twitter server did not respond to the request.',
        
        'error_button_down' : 'Twitter is offline',
        'error_down' :
            'Could not establish a connection to the Twitter server.',
        
        'error_button_rate_limit' : 'Ratelimit exceeded',
        'error_rate_limit' :
            'Twitters limit on requests has been exceeded.\n'
            'Automatic refresh in %d minute(s).',
        
        'error_template' : '<b>Error from %H:%M:%S</b>\n',
        
        # Warning Dialogs
        'warning_title' : 'Atarashii - Warning',

        'warning_button_rate_limit' : 'Rate limit reduced',
        'warning_rate_limit' :
            'Twitter has lowered the rate limit to %d requests per '
            'hour, the update interval has been adjusted accordingly.',
        
        'warning_button_overload' : 'Twitter is over capacity',
        'warning_overload' :
            'Atarashii couldn\'t connect to Twitter, in most cases '
            'this is just a temporary issue due to Twitter being too '
            'busy at the moment.',
        
        'warning_button_network' : 'Network error',
        'warning_network' :
            'Atarashii has lost the conntection to the Internet. It '
            'will automatically try to reconnect itself every 60 seconds.',
        
        'warning_network_timeout' :
            'Atarashii has lost the conntection to Twitter. It '
            'will automatically try to reconnect itself every 60 seconds.',
        
        'warning_template' : '<b>Warning from %H:%M:%S</b>\n',
        
        # Buttons
        'button_open' : 'Clock for more information',
        
        # Toolbar items
        'tool_refresh' : 'Refresh Tweets',
        'tool_history' : 'Reset History',
        'tool_read' : 'Mark all Tweets as read',
        'tool_mode' : 'Messages',
        'tool_settings' : 'Open Preferences',
        'tool_about' : 'About Atarashii',
        'tool_quit' : 'Quit Atarashii',
        'tool_refresh_message' : 'Refresh Message',
        'tool_history_message' : 'Remove History',
        'tool_read_message' : 'Mark all Messages as read',
        
        # Tray Menu
        'menu_update' : 'Refresh',
        'menu_read' : 'Mark all as read',
        'menu_settings' : 'Preferences',
        'menu_about' : 'About Atarashii',
        'menu_quit' : 'Quit',
        
        # Tray Tooltip
        'tray_title' : 'Atarashii',
        'tray_logging_in' : 'Connecting as <b>%s</b>...',
        'tray_logged_out' : 'Not connected.',
        'tray_logged_in' : 'Logged in as <b>%s</b>.',
        
        'tray_tweet' : '<b>%d</b> new Tweet',
        'tray_message' : '<b>%d</b> new Message',
        'tray_tweets' : '<b>%d</b> new Tweets',
        'tray_messages' : '<b>%d</b> new Messages',
        
        # These are shown in the notifications, tags get removed
        'tray_error_login' : 'Login as <b>%s</b> failed.',
        'tray_error_rate' : 'Request limit exceeded.',
        'tray_warning_network' : '<b>Network error.</b>',
        'tray_warning_twitter' : '<b>Twitter is over capacity.</b>',
        'tray_error_twitter' : 'Twitter server error.',
        'tray_error_down' : 'Twitter is offline.',
        'tray_error_rate_limit' : 'Ratelimit exceeded.',
        
        # Context Menu
        'context_browser' : 'Open in Browser',
        'context_copy' : 'Copy link location',
        'context_copy_tweet' : 'Copy Tweet',
        'context_copy_message' : 'Copy Message',
        'context_profile' : 'Visit %s on Twitter.com',
        'context_reply' : 'Reply to %s...',
        'context_tweet' : 'Tweet to %s...',
        'context_message' : 'Message to %s...',
        'context_source' : '%s Homepage',
        'context_view' : 'View on Twitter.com',
        'context_search' : 'Search on Twitter.com',
        'context_retweet_old' : 'Retweet %s via RT',
        'context_retweet_new' : 'Retweet %s via Twitter',
        'context_delete_tweet' : 'Delete Tweet',
        'context_delete_message' : 'Delete Message',
        'context_edit_tweet' : 'Edit Tweet'
    }
}


class Language:
    def __init__(self, code):
        if LANG.has_key(code):
            stuff = LANG[code]
        
        else:
            stuff = LANG['en_US']
        
        # set instance fields
        for key, value in stuff.iteritems():
            self.__dict__[key] = value

# Select Language
LANG = Language(locale.getdefaultlocale()[0])
