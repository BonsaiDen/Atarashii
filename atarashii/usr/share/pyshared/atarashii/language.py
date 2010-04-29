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
import sys


class Language(object):
    def __init__(self, code):
        try:
            code = sys.argv[sys.argv.index('-l') + 1]
        
        except ValueError:
            pass
        
        stuff = LANG[code] if code in LANG else LANG['en']
        for key, value in stuff.iteritems():
            setattr(self, key, value)


LANG = {
    
    
    # German -------------------------------------------------------------------
    # --------------------------------------------------------------------------
    'de': {
        
        # Title
        'title': 'Atarashii',
        'title_logged_in': '%s - Atarashii',
        'title_logging_in': 'Verbinde als %s...',
        
        # Tabs
        'tabs_tweets': 'Tweets',
        'tabs_tweets_new': 'Tweets <b>(%d)</b>',
        'tabs_messages': 'Nachrichten',
        'tabs_messages_new': 'Nachrichten <b>(%d)</b>',
        
        # Username
        'name': lambda x: x + '\'' if x[-1:] in 'xs' else x + 's',
        
        # Tweets
        'tweet_hash': '#',
        'tweet_at': '@',
        
        # HTML
        'html_welcome': 'Willkommen bei Atarashii.',
        'html_loading': 'Tweets werden geladen...',
        
        'html_account':
            'Derzeit ist kein Account aktiviert.',
        
        'html_account_info':
            'Klicken sie auf das Atarashii Symbol in Ihrer Taskleiste und '
            'wählen sie "Einstellungen" um einen Account zu erstellen und/oder'
            ' wählen sie "Accounts" und aktivieren Sie einen der vorhandenen.',
        
        'html_avatar_tooltip':
            '<span size="large"><b>%s</b></span>\n<b>%d</b> Tweets\n'
            '<b>%d</b> Follower\nFollowing <b>%d</b>',
        
        'html_expanded_tooltip': '<b>%s</b> verweist auf:\n%s',
        
        'html_profile': '%s Profil betrachten',
        'html_at': '%s Profil betrachten',
        'html_reply': '%s antworten',
        'html_retweet': '%s retweeten',
        'html_favorite': 'Favorisieren!',
        'html_unfavorite': 'Normalisieren',
        'html_time': 'Getwittert um %H:%M:%S Uhr',
        'html_time_day': 'Getwittert am %d.%m.%Y um %H:%M:%S Uhr',
        'html_time_message': 'Gesendet um %H:%M:%S Uhr',
        'html_time_day_message': 'Gesendet am %d.%m.%Y um %H:%M:%S Uhr',
        'html_search': 'Suche nach &quot;%s&quot;',
        'html_by': ' &lceil;%s&rfloor;',
        'html_in_reply': 'in Antwort auf %s',
        'html_in_reply_view': 'Antwort auf Twitter.com betrachten',
        'html_in_retweet': 'retweeted von %s',
        'html_load_more': 'Mehr',
        'html_empty': 'Keine Tweets.',
        'html_protected': '%s Tweets sind geschützt',
        'html_about_second': 'vor ca. einer Sekunde',
        'html_second': 'vor %d Sekunden',
        'html_about_minute': 'vor ca. einer Minute',
        'html_minute': 'vor %d Minuten',
        'html_about_hour': 'vor ca. einer Stunde',
        'html_hour': 'vor %d Stunden',
        'html_about_day': 'vor ca. einem Tag',
        'html_day': 'vor %d Tagen',
        'html_yesterday': 'von Gestern',
        'html_exact': 'vom %d.%m.%Y',
        
        # Profile
        'profile_loading': '<b>%s</b> Profil wird geladen...',
        'profile_close': '<b>%s</b> Profil schliessen',
        'profile_link': 'Auf Twitter.com',
        'profile_name': '<b>%s</b> (%s)',
        'profile_info':
            '<b><span size="large">%s</span></b>\n'
            '<b>%d</b> Tweets\n<b>%d</b> Follower\nFollowing <b>%d</b>',
        
        'profile_website': '<b>Web:</b> <a href="%s">%s</a>',
        'profile_location': '<b>Ort:</b> %s',
        'profile_description': '<b>Bio:</b> %s',
        'profile_follows_you': '(<b>auch Ihnen</b>)',
        'profile_protected': '(<b>geschützt</b>)',
        
        'profile_error':
            '<b>%s</b> Profil konnte nicht geladen werden, der Benutzer '
            'existiert entweder nicht oder Twitter ist gerade nicht '
            'erreichbar.',
        
        'profile_tweets': 'Tweets',
        'profile_followers': 'Follower',
        'profile_following': 'Following',
        
        'profile_follow': 'Followen',
        'profile_unfollow': 'Unfollowen',
        'profile_block': 'Blocken',
        'profile_unblock': 'Unblocken',
        'profile_message': 'Nachricht',
        
        'profile_html_protected': 'Tweets sind geschützt.',
        'profile_html_loading': 'Profil wird geladen...',
        'profile_html_empty': 'Keine aktuellen Tweets',
        'profile_html_load_more': 'Mehr',
        
        # Messages
        'message_loading': 'Nachrichten werden geladen...',
        'message_load_more': 'Mehr',
        'message_empty': 'Keine Nachrichten.',
        'message_from': 'Von',
        'message_to': 'An',
        
        # Notifications
        'notification_message': 'Nachricht von %s',
        'notification_index': '%s (%d von %d)', # 'Message (3 of 4)'
        'notification_login': '%s wurde angemeldet',
        'notification_login_tweet': '%d ungelesener Tweet',
        'notification_login_message': '%d ungelesene Nachricht',
        'notification_login_tweets': '%d ungelesene Tweets',
        'notification_login_messages': '%d ungelesene Nachrichten',
        
        # Textbox
        'text_entry': 'Was passiert gerade?',
        'text_entry_message': 'Nachricht eingeben...',
        
        # Statusbar
        'status_logout': 'Nicht verbunden.',
        'status_connecting': 'Verbinde als %s...',
        'status_connected': 'Verbunden, aktualisiere...',
        'status_error': 'Verbindung fehlgeschlagen.',
        'status_seconds': 'Aktualisierung in %s Sekunden.',
        'status_one_second': 'Aktualisierung in einer Sekunde.',
        'status_minute': 'Aktualisierung in einer Minute.',
        'status_minutes': 'Aktualisierung in %d Minuten.',
        'status_update': 'Aktualisiere...',
        'status_reply': 'Antworte %s...',
        'status_retweet': 'Retweete %s...',
        'status_message': 'Sende Nachricht an %s...',
        'status_message_reply': 'Antworte %s...',
        'status_send': 'Sende Status...',
        'status_profile': 'Lade %s Profil...',
        'status_left': 'Noch %d Zeichen.',
        'status_more': '%d Zeichen zu viel.',
        'status_more_tweet': '%d Zeichen zu viel, %d mehr um zu teilen.',
        'status_more_message': '%d Zeichen zu viel, %d mehr um zu teilen.',
        'status_more_tweet_split': '%d Zeichen zu viel. Tweet wird geteilt.',
        'status_more_message_split':
            '%d Zeichen zu viel. Nachricht wird geteilt.',
        
        'status_load_history': 'Tweets werden geladen...',
        'status_load_message_history': 'Nachrichten werden geladen...',
        'status_reconnect_seconds': 'Automatischer Reconnect in %d Sekunden.',
        'status_reconnect_minute': 'Automatischer Reconnect in einer Minute.',
        'status_reconnect_minutes': 'Automatischer Reconnect in %d Minuten.',
        'status_deleting_tweet': 'Lösche Tweet...',
        'status_deleting_message': 'Lösche Nachricht...',
        'status_edit': 'Bearbeite Tweet...',
        'status_edit_reply': 'Bearbeite Antwort an %s...',
        
        # Info Label
        'label_reply': '<b>Tweet an %s:</b>',
        'label_reply_text': '<b>Antwort auf:</b> %s',
        'label_retweet': '<b>%s retweeten:</b>',
        'label_message': '<b>Nachricht an %s:</b>',
        'label_message_text': '<b>Antwort auf:</b> %s',
        'label_edit': '<b>Tweet bearbeiten:</b> %s',
        'label_edit_reply': '<b>Antwort an %s bearbeiten:</b> %s',
        
        # Settings Dialog
        'settings_title': 'Atarashii - Einstellungen',
        'settings_button': 'Speichern',
        'settings_buttonCancel': 'Abbrechen',
        'settings_tab_general': 'Allgemein',
        'settings_tab_accounts': 'Accounts',
        'settings_tab_notifications': 'Benachrichtigungen',
        'settings_tab_theme': 'Thema',
        'settings_tab_atarashii': 'Atarashii',
        'settings_tab_syncing': 'Synchronisation',
        'settings_notifications_enable': 'Benachrichtigungen Aktivieren',
        'settings_notifications_overlay': 'Abspielen Filme überlagern',
        'settings_notifications_sound': 'Sounds abspielen',
        'settings_file_tweets': 'Tweets:',
        'settings_file_replies': 'Antworten:',
        'settings_file_messages': 'Nachrichten:',
        'settings_file_info': 'Sonstige:',
        'settings_file': 'Soundatei auswählen',
        'settings_file_none': '...',
        'settings_file_filter': 'Soundateien',
        'settings_autostart': 'Atarashii beim Login starten',
        'settings_tray': 'Minimiert starten(System Tray)',
        'settings_taskbar': 'Atarashii in der Taskleiste anzeigen',
        'settings_info_sound': 'Info Sounds abspielen',
        'settings_shortener': 'URL-Kürzer:',
        'settings_shortener_off': 'Deaktiviert',
        'settings_continue': 'Fortsetzungszeichen:',
        'settings_continue_names': ['Punkte', 'Strich', 'Tilde', 'Pfeil'],
        'settings_avatar_size': 'Avatargröße:',
        'settings_font_size': 'Schriftgröße:',
        'settings_color_theme': 'Farbschema:',
        'settings_add': 'Erstellen',
        'settings_edit': 'Bearbeiten',
        'settings_delete': 'Löschen',
        'settings_file_ok': 'OK',
        'settings_file_cancel': 'Abbrechen',
        'settings_sync': 'Syncing',
        
        # Syncing Dialog
        'sync_checkbutton': 'Synchronisation aktivieren',
        'sync_key_current': '<b>Derzeitiges Sync-Token</b>',
        'sync_key_changed': '<b>Derzeitiges Sync-Token(geändert)</b>',
        'sync_key_error': '<b>Fehler</b>',
        'sync_key_loading': '<b>Lade Sync-Token...</b>',
        'sync_key_no': '<b>Kein Sync-Token gesetzt.</b>',
        'sync_key_failed': 'Sync-Token konnte nicht empfangen werden.',
        'sync_key_label': '<b><span size="large">%s</span></b>',
        'sync_new': 'Neues Token',
        'sync_cancel': 'Abbrechen',
        'sync_ok': 'OK',
        'sync_change': 'Ändern',
        'sync_key_enter': 'Vorhandenes Sync-Token eingeben:',
        
        'sync_button_down': 'Synchronisation fehlgeschlagen',
        'sync_warning_down':
            'Atarashii konnte die Synchronisationsdaten nicht <b>abrufen</b>.'
            '\nDies ist in den meisten Fällen lediglich ein temporäres '
            'Problem.',
        
        'sync_button_up': 'Synchronisation fehlgeschlagen',
        'sync_warning_up':
            'Atarashii konnte die Synchronisationsdaten nicht <b>senden</b>.\n'
            'Dies ist in den meisten Fällen lediglich ein temporäres '
            'Problem.',
        
        'sync_button_key': 'Synchronisation fehlgeschlagen',
        'sync_error_key':
            'Ihr Sync-Token ist ungültig, bitte rufen Sie die Einstellungen '
            'auf und generieren sie ein neues.\n\nSync-Tokens verfallen falls '
            'sie in den ersten 24 Stunden nach Ihrer Generierung nicht benutzt'
            ' wurden.',
        
        'sync_user_error_title': 'Ungültiges Token',
        'sync_user_error':
            'Es wurden keine Synchronisationsdaten für das eingebene '
            'Token gefunden, bitte überprüfen Sie ob es korrekt ist.',
        
        # About Dialog
        'about_title': 'Info zu Atarashii',
        'about_okbutton': 'OK',
        'about_kitten_button': 'Kittens',
        'about_back_button': 'Zurück',
        'about_description':
            'Twitter Client für den GNOME Desktop.',
        
        'about_kittens':
            '<span size="small">This Version was packaged by <b>%s</b> '
            'kittens.</span>\n<span size="small">Their lucky number is '
            '<b>%s</b>!</span>',
        
        # Account Dialog
        'account_edit': 'Benutzer bearbeiten',
        'account_create': 'Benutzer erstellen',
        'account_delete': 'Benutzer löschen',
        'account_delete_description':
            'Möchten sie den Benutzer <b>%s</b> wirklich löschen?',
        
        'account_button': 'OK',
        'account_button_cancel': 'Abbrechen',
        'account_username': 'Benutzername:',
        
        # Password Dialog
        'password_button': 'OK',
        'password_button_cancel': 'Abbrechen',
        'password_title': 'Passwort',
        'password_question': '<b>%s</b> Passwort:',
        'password_too_short': '<i><b>Fehler:</b> Mindestens 6 Zeichen.</i>',
        
        # Retweet Dialogs
        'retweet_button': 'Retweet erfolgreich',
        
        # Follow Dialogs
        'follow_button': '<b>%s</b> wird nun gefollowed',
        'unfollow_button': '<b>%s</b> wird nicht mehr gefollowed',
        'error_follow': '<b>%s</b> konnte nicht gefollowed werden.',
        'error_unfollow': '<b>%s</b> konnte nicht unfollowed werden.',
        
        # Block Dialogs
        'block_button': '<b>%s</b> wird nun geblockt',
        'block_button_spam': '<b>%s</b> wird nun geblockt und wurde gemeldet',
        'unblock_button': '<b>%s</b> wird nicht mehr geblockt',
        'error_block': '<b>%s</b> konnte nicht geblockt werden.',
        'error_unblock': '<b>%s</b> konnte nicht entblockt werden.',
        'block_user_spam':
            'Möchten Sie <b>%s</b> zusätzlich noch wegen '
            'Spam/Missbrauch melden?',
        
        'block_title': 'Benutzer blocken',
        
        # Delete Dialogs
        'delete_title': 'Löschen bestätigen',
        'delete_tweet_question':
            '<b>Diesen Tweet wirklich löschen?</b>\n<i>%s</i>',
        
        'delete_message_question':
            '<b>Diese Nachricht wirklich löschen?</b>\n<i>%s</i>',
        
        'delete_button_message': 'Nachricht gelöscht',
        'delete_button_tweet': 'Tweet gelöscht',
        
        # Crash Error Dialogs
        'error_general':
            '<span size="large"><b>Atarashii ist abgestürzt...</b></span>\n'
            '...hat sich aber automatisch neu gestartet!\n\n'
            'Im Normalfall sollten keine Daten verloren gegangen sein.\n\n',
        
        'error_crashed_title': 'Keizoku wa chikara nari',
        'error_crashed':
            'Es handelt sich um einen <b>externen</b> Fehler mit dem Code '
            '<b>%s</b>, mehr konnten die Kätzchen leider nicht herausfinden.',
        
        'error_crashed__python_title': 'Snake? Snake? Snaaaaaaaaaaake!',
        'error_crashed_python':
            'Es handelt sich um einen <b>internen</b> Fehler das Log finden '
            'Sie <a href="file://%s">hier</a>.',
        
        # User Errors
        'error_title': 'Atarashii - Fehler',
        'error_login':
            'Die Anmeldung als <b>%s</b> ist fehlgeschlagen.',
        
        'error_already_retweeted':
            'Dieser Tweet wurde bereits von Ihnen retweeted.',
        
        'error_user_not_found': 'Der Benutzer <b>%s</b> existiert nicht.',
        'error_user_not_follow':
            'Sie können keine Nachrichten an Benutzer schicken die ihnen nicht'
            ' followen.',
        
        'error_duplicate': 'Sie haben dies bereits getweetet.',
        'error_tweet_not_found': 'Dieser Tweet wurde bereits gelöscht.',
        'error_message_not_found': 'Diese Nachricht wurde bereits gelöscht.',
        
        'error_network':
            'Atarashii konnte keine Verbindung zum Internet herstellen.',
        
        'error_network_timeout':
            'Atarashii konnte keine Verbindung zu Twitter herstellen.',
        
        'error_favorite_on':
            '<b>%s</b> Tweet konnte nicht favorisiert werden.',
        
        'error_favorite_off':
            '<b>%s</b> Tweet konnte nicht entfavorisiert werden.',
        
        'error_ratelimit_reconnect':
            'Twitter Requestlimit wurde überschritten.\n'
            'Verbinde automatisch neu in %d Minute(n).',
        
        # Error Button stuff
        'error_button_twitter': 'Twitter Serverfehler',
        'error_twitter':
            'Der Twitter Server hat keine Antwort gesendet.',
        
        'error_button_down': 'Twitter ist derzeit offline',
        'error_down': 'Twitter konnte nicht erreicht werden.',
        
        'error_button_rate_limit': 'Requestlimit überschritten',
        'error_rate_limit':
            'Twitter Requestlimit wurde überschritten.\n'
            'Automatische Aktualisierung in %d Minute(n).',
        
        'error_template': '<b>Fehler von %H:%M:%S:</b>\n',
        
        # Warning Dialogs
        'warning_title': 'Atarashii - Warnung',
        
        'warning_button_rate_limit': 'Requestlimit verringert',
        'warning_rate_limit':
            'Twitter hat das Requestlimit auf %d Requests pro Stunde '
            'reduziert, das Aktualisierungsinterval wurde '
            'entsprechend angepasst.',
        
        'warning_button_overload': 'Twitter überlastet',
        'warning_overload':
            'Twitter ist derzeit überlastet, dies ist in '
            'den meisten Fällen lediglich ein temporäres Problem und sollte '
            'nur einige Minuten anhalten.',
        
        'warning_button_network': 'Netzwerkfehler',
        'warning_network':
            'Atarashii konnte keine Verbindung zum Internet herstellen.',
        
        'warning_network_timeout':
            'Atarashii hat die Verbindung zu Twitter verloren, dies ist in '
            'den meisten Fällen lediglich ein temporäres Problem '
            'aufgrund von Überlastung seitens Twitter.',
        
        'warning_network_twitter':
            'Atarashii konnte keine Verbindung zu Twitter herstellen.',
        
        'warning_template': '<b>Warnung von %H:%M:%S:</b>\n',
        
        # Info Button
        'info_title': '',
        'info_template': '',
        
        # Buttons
        'button_open': 'Für weitere Informationen klicken',
        'button_remove': 'Zum entfernen klicken',
        
        # Multibutton
        'multi_refresh': 'Tweets aktualisieren',
        'multi_history': 'Ältere Tweets zurücksetzen',
        'multi_read': 'Alle Tweets als gelesen markieren',
        'multi_refresh_message': 'Nachrichten aktualisieren',
        'multi_history_message': 'Ältere Nachrichten entfernen',
        'multi_read_message': 'Alle Nachrichten als gelesen markieren',
        
        # Tray Menu
        'menu_update': 'Akualisie_ren',
        'menu_read': 'Alle als gelesen _markieren',
        'menu_settings': '_Einstellungen',
        'menu_about': '_Info',
        'menu_accounts': '_Accounts',
        'menu_logout': 'Ausl_oggen',
        'menu_quit': '_Beenden',
        
        # Tray Tooltip
        'tray_title': 'Atarashii',
        'tray_logging_in': 'Verbinde als <b>%s</b>...',
        'tray_logged_out': 'Nicht verbunden.',
        'tray_logged_in': 'Angemeldet als <b>%s</b>.',
        
        'tray_tweet': '<b>%d</b> ungelesener Tweet',
        'tray_message': '<b>%d</b> ungelesene Nachricht',
        'tray_tweets': '<b>%d</b> ungelesene Tweets',
        'tray_messages': '<b>%d</b> ungelesene Nachrichten' ,
        
        # These are shown in the notifications, tags get removed
        'tray_error_login': 'Anmeldung als <b>%s</b> fehlgeschlagen.',
        'tray_error_rate': 'Requestlimit überschritten.',
        'tray_warning_network': '<b>Netzwerkfehler.</b>',
        'tray_warning_overload': '<b>Twitter ist überlastet.</b>',
        'tray_warning_timeout': '<b>Netzwerkfehler.</b>',
        'tray_warning_twitter': '<b>Twitter ist nicht zu erreichen.</b>',
        'tray_error_twitter': 'Twitter Serverfehler.',
        'tray_error_down': 'Twitter ist derzeit offline.',
        'tray_error_rate_limit': 'Requestlimit überschritten.',
        
        # Context Menu
        'content_block': '%s blockieren',
        'content_unfollow': '%s entfolgen',
        'context_browser': 'Im _Browser öffnen',
        'context_copy': 'Link _kopieren',
        'context_copy_tweet': 'Tweet _kopieren',
        'context_copy_message': 'Nachricht _kopieren',
        'context_copy_tag': 'Hashtag _kopieren',
        'context_profile': '%s auf Twitter.com',
        'context_reply': '%s _antworten...',
        'context_tweet': '_Tweet an %s...',
        'context_message': '_Nachricht an %s...',
        'context_source': '%s _Homepage',
        'context_view': 'Auf Twitter.com aufrufen',
        'context_search': 'Auf Twitter.com suchen',
        'context_retweet_old': '%s via _RT retweeten',
        'context_retweet_new': '%s via _Twitter retweeten',
        'context_delete_tweet': 'Tweet _löschen',
        'context_delete_message': 'Nachricht _löschen',
        'context_edit_tweet': 'Tweet _bearbeiten',
        'context_friend_loading': 'Status abfragen...',
        'context_friend_follow': '%s followen',
        'context_friend_unfollow': '%s unfollowen',
        'context_friend_block': '%s blocken',
        'context_friend_unblock': '%s unblocken'
    },
    
    
    # English ------------------------------------------------------------------
    # --------------------------------------------------------------------------
    'en': {
        
        # Title
        'title': 'Atarashii',
        'title_logged_in': '%s - Atarashii',
        'title_logging_in': 'Connecting as %s...',
        
        # Tabs
        'tabs_tweets': 'Tweets',
        'tabs_tweets_new': 'Tweets <b>(%d)</b>',
        'tabs_messages': 'Messages',
        'tabs_messages_new': 'Messages <b>(%d)</b>',
        
        # Username
        'name': lambda x: x + '\'s' if x[-1:] in 'xs' else x + 's',
        
        # Tweets
        'tweet_hash': '#',
        'tweet_at': '@',
        
        # HTML
        'html_welcome': 'Welcome to Atarashii.',
        'html_loading': 'Loading Tweets...',
        
        'html_account':
            'No Account is currently activated.',
        
        'html_account_info':
            'Click on the Atarashii icon in your Taskbar and select '
            '"Preferences" in order to create an Account and/or select '
            '"Accounts" to choose from a list of already existing ones.',
        
        'html_avatar_tooltip':
            '<span size="large"><b>%s</b></span>\n<b>%d</b> Tweets\n'
            '<b>%d</b> Followers\nFollowing <b>%d</b>',
        
        'html_expanded_tooltip': '<b>%s</b> redirects to:\n%s',
        
        'html_profile': 'View %s profile',
        'html_at': 'View %s profile',
        'html_reply': 'Reply to %s',
        'html_retweet': 'Retweet %s',
        'html_favorite': 'Favorite!',
        'html_unfavorite': 'Normalize',
        'html_time': 'Tweeted at %H:%M:%S',
        'html_time_day': 'Tweeted on %m.%d.%Y at %H:%M:%S',
        'html_time_message': 'Sent at %H:%M:%S',
        'html_time_day_message': 'Sent on %m.%d.%Y at %H:%M:%S',
        'html_search': 'Search for &quot;%s&quot;',
        'html_by': ' &lceil;%s&rfloor;',
        'html_in_reply': 'in reply to %s',
        'html_in_reply_view': 'View Reply on Twitter.com',
        'html_in_retweet': 'retweeted by %s',
        'html_load_more': 'More',
        'html_empty': 'No Tweets.',
        'html_protected': '%s\'s Tweets are protected',
        'html_about_second': 'about one second ago',
        'html_second': '%d seconds ago',
        'html_about_minute': 'about a minute ago',
        'html_minute': '%d minutes ago',
        'html_about_hour': 'about an hour ago',
        'html_hour': '%d hours ago',
        'html_about_day': 'about a day ago',
        'html_day': '%d days ago',
        'html_yesterday': 'from yesterday',
        'html_exact': 'from %m.%d.%Y',
        
        # Profile
        'profile_loading': 'Loading <b>%s</b> profile...',
        'profile_close': 'Close <b>%s</b> profile',
        'profile_link': 'On Twitter.com',
        'profile_name': '<b>%s</b> (%s)',
        'profile_info':
            '<b><span size="large">%s</span></b>\n'
            '<b>%d</b> Tweets\n<b>%d</b> Followers\nFollowing <b>%d</b>',
        
        'profile_website': '<b>Web:</b> <a href="%s">%s</a>',
        'profile_location': '<b>Location:</b> %s',
        'profile_description': '<b>Bio:</b> %s',
        'profile_follows_you': '(<b>you too</b>)',
        'profile_protected': '(<b>protected</b>)',
        
        'profile_error':
            'Could not load <b>%s</b> profile, either the user does not exist '
            'or Twitter is currently unavailable.',
        
        'profile_tweets': 'Tweets',
        'profile_followers': 'Followers',
        'profile_following': 'Following',
        
        'profile_follow': 'Follow',
        'profile_unfollow': 'Unfollow',
        'profile_block': 'Block',
        'profile_unblock': 'Unblock',
        'profile_message': 'Message',
        
        'profile_html_protected': 'Tweets are protected.',
        'profile_html_loading': 'Loading profile...',
        'profile_html_empty': 'No recent Tweets.',
        'profile_html_load_more': 'More',
        
        # Messages
        'message_loading': 'Loading messages...',
        'message_load_more': 'More',
        'message_empty': 'No Messages.',
        'message_from': 'From',
        'message_to': 'To',
        
        # Notifications
        'notification_message': 'Message from %s',
        'notification_index': '%s (%d of %d)',
        'notification_login': '%s has logged in',
        'notification_login_tweet': '%d unread Tweet',
        'notification_login_message': '%d unread Message',
        'notification_login_tweets': '%d unread Tweets',
        'notification_login_messages': '%d unread Messages',
        
        # Textbox
        'text_entry': 'What\'s happening?',
        'text_entry_message': 'Enter Message...',
        
        # Statusbar
        'status_logout': 'Not connected.',
        'status_connecting': 'Connecting as %s...',
        'status_connected': 'Connected, refreshing...',
        'status_error': 'Connection failed.',
        'status_seconds': 'Refresh in %s seconds.',
        'status_one_second': 'Refresh in one second.',
        'status_minute': 'Refresh in one minute.',
        'status_minutes': 'Refresh in %d minutes.',
        'status_update': 'Refreshing...',
        'status_reply': 'Replying to %s...',
        'status_retweet': 'Retweeting %s...',
        'status_message': 'Sending Message to %s...',
        'status_message_reply': 'Replying to %s...',
        'status_send': 'Sending Status...',
        'status_profile': 'Loading %s profile...',
        'status_left': '%d char(s) left.',
        'status_more': 'Plus %d char(s).',
        'status_more_tweet': 'Plus %d char(s), %d till split.',
        'status_more_message': 'Plus %d char(s), %d till split.',
        'status_more_tweet_split': 'Plus %d char(s). Tweet will be split.',
        'status_more_message_split': 'Plus %d char(s). Message will be split.',
        'status_load_history': 'Loading Tweets...',
        'status_load_message_history': 'Loading Messages...',
        'status_reconnect_seconds': 'Automatic reconnect in %d seconds.',
        'status_reconnect_minute': 'Automatic reconnect in one minute.',
        'status_reconnect_minutes': 'Automatic reconnect in %d minutes.',
        'status_deleting_tweet': 'Deleting Tweet...',
        'status_deleting_message': 'Deleting Message...',
        'status_edit': 'Editing Tweet...',
        'status_edit_reply': 'Editing Reply to %s...',
        
        # Info Label
        'label_reply': '<b>Tweet to %s:</b>',
        'label_reply_text': '<b>Reply on:</b> %s',
        'label_retweet': '<b>Retweet %s:</b>',
        'label_message': '<b>Message to %s:</b>',
        'label_message_text': '<b>Message on:</b> %s',
        'label_edit': '<b>Edit Tweet:</b> %s',
        'label_edit_reply': '<b>Edit Reply to %s:</b> %s',
        
        # Settings Dialog
        'settings_title': 'Atarashii - Preferences',
        'settings_button': 'Save',
        'settings_buttonCancel': 'Cancel',
        'settings_tab_general': 'General',
        'settings_tab_accounts': 'Accounts',
        'settings_tab_notifications': 'Notifications',
        'settings_tab_theme': 'Theme',
        'settings_tab_atarashii': 'Atarashii',
        'settings_tab_syncing': 'Synchronization',
        'settings_notifications_enable': 'Enable notifications',
        'settings_notifications_overlay': 'Overlay playing movies',
        'settings_notifications_sound': 'Play sounds',
        'settings_file_tweets': 'Tweets:',
        'settings_file_replies': 'Replies:',
        'settings_file_messages': 'Messages:',
        'settings_file_info': 'Other:',
        'settings_file': 'Select soundfile',
        'settings_file_none': '...',
        'settings_file_filter': 'Soundfiles',
        'settings_autostart': 'Launch Atarashii on user login',
        'settings_tray': 'Start minimized(system tray)',
        'settings_taskbar': 'Show Atarashii in the Taskbar',
        'settings_info_sound': 'Play info sounds',
        'settings_shortener': 'URL-Shortener:',
        'settings_shortener_off': 'Deactivated',
        'settings_continue': 'Cont. character:',
        'settings_continue_names': ['Points', 'Hypen', 'Tilde', 'Arrow'],
        'settings_avatar_size': 'Avatar size:',
        'settings_font_size': 'Font size:',
        'settings_color_theme': 'Color scheme:',
        'settings_add': 'Add',
        'settings_edit': 'Edit',
        'settings_delete': 'Delete',
        'settings_file_ok': 'OK',
        'settings_file_cancel': 'Cancel',
        'settings_sync': 'Syncing',
        
        # Syncing Dialog
        'sync_checkbutton': 'Activate synchronization',
        'sync_key_current': '<b>Current Sync-Token</b>',
        'sync_key_changed': '<b>Current Sync-Token(changed)</b>',
        'sync_key_loading': '<b>Loading Sync-Token...</b>',
        'sync_key_no': '<b>No Sync-Token set.</b>',
        'sync_key_error': '<b>Error</b>',
        'sync_key_failed': 'Failed to retrieve Sync-Token.',
        'sync_key_label': '<b><span size="large">%s</span></b>',
        'sync_new': 'New Token',
        'sync_cancel': 'Cancel',
        'sync_ok': 'OK',
        'sync_change': 'Change',
        'sync_key_enter': 'Enter an existing Sync-Token:',
        
        'sync_button_down': 'Synchronization failed',
        'sync_warning_down':
            'Atarashii could not <b>retrieve</b> the synchronization data.\n'
            'In most cases this is just a temporary problem.',
        
        'sync_button_up': 'Synchronization failed',
        'sync_warning_up':
            'Atarashii could not <b>send</b> the synchronization data.\n'
            'In most cases this is just a temporary problem.',
        
        'sync_button_key': 'Synchronization failed',
        'sync_error_key':
            'Your Sync-Token is invalid, please go to the preferences and '
            'request a new one.\n\nSync-Tokens do <b>expire</b> when they '
            'havn\'t been used in the first <b>24 hours</b> after their '
            'generation.',
        
        'sync_user_error_title': 'Invalid Token',
        'sync_user_error':
            'No synchronisation data for the entered Sync-Token was found, '
            'please make sure that you have entered the token correctly.',
        
        # About Dialog
        'about_title': 'About Atarashii',
        'about_okbutton': 'OK',
        'about_kitten_button': 'Kittens',
        'about_back_button': 'Back',
        'about_description':
            'Twitter Client for the GNOME Desktop.',
        
        'about_kittens':
            '<span size="small">This Version was packaged by <b>%s</b> '
            'kittens.</span>\n<span size="small">Their lucky number is '
            '<b>%s</b>!</span>',
        
        # Account Dialog
        'account_edit': 'Edit user',
        'account_create': 'Create a new user',
        'account_delete': 'Delete user',
        'account_delete_description':
        'Do you really want to delete the user <b>%s</b>?',
        
        'account_button': 'OK',
        'account_button_cancel': 'Cancel',
        'account_username': 'Username:',
        'password_button': 'OK',
        'password_button_cancel': 'Cancel',
        'password_title': 'Password',
        'password_question': '<b>%s</b> password:',
        'password_too_short': '<i><b>Error:</b> At least 6 characters.</i>',
        
        # Retweet Dialogs
        'retweet_button': 'Retweet successful',
        
        # Follow Dialogs
        'follow_button': 'You now follow <b>%s</b>',
        'unfollow_button': 'You no longer follow <b>%s</b>',
        'error_follow': 'Could not follow <b>%s</b>.',
        'error_unfollow': 'Could not unfollow <b>%s</b>.',
        
        # Block Dialogs
        'block_button': '<b>%s</b> has been blocked',
        'block_button_spam': '<b>%s</b> has been blocked and reported',
        'unblock_button': '<b>%s</b> has been unblocked',
        'error_block': 'Could not block <b>%s</b>.',
        'error_unblock': 'Could not unblock <b>%s</b>.',
        'block_user_spam':
            'Do you want to report <b>%s</b> for spam/abuse?',
        
        'block_title': 'Block user',
        
        # Delete Dialogs
        'delete_title': 'Confirm delete',
        'delete_tweet_question':
            '<b>Are you sure to delete this Tweet?</b>\n<i>%s</i>',
        
        'delete_message_question':
            '<b>Are you sure to delete this Message?</b>\n<i>%s</i>',
        
        'delete_button_message': 'Message deleted',
        'delete_button_tweet': 'Tweet deleted',
        
        # Crash Error Dialogs
        'error_general':
            '<span size="large"><b>Atarashii has crashed...</b></span>\n'
            '...but it has automatically restarted itself!\n\n'
            'In the normal case no data was lost.\n\n',
        
        'error_crashed_title': 'Keizoku wa chikara nari',
        'error_crashed':
            'The error was an <b>external</b> one with the code <b>%s</b>,'
            ' that\'s all the Kittens could find out.',
        
        'error_crashed__python_title': 'Snake? Snake? Snaaaaaaaaaaake!',
        'error_crashed_python':
            'The error was an <b>internal</b> one, you\'ll find the log '
            '<a href="file://%s">here</a>.',
        
        # User Errors
        'error_title': 'Atarashii - Error',
        'error_login': 'The login as <b>%s</b> has failed.',
        'error_already_retweeted':
            'You\'ve already retweeted this Tweet.',
        
        'error_user_not_found': 'The user <b>%s</b> does not exist.',
        'error_user_not_follow':
            'You cannot send messages to users that don\' follow you.',
        
        'error_duplicate': 'You\'ve already tweeted this.',
        'error_tweet_not_found': 'This Tweet has already been deleted.',
        'error_message_not_found': 'This Message has already been deleted.',
        
        'error_network':
            'Atarashii could not establish a connection to the Internet.',
        
        'error_network_timeout':
            'Atarashii could not establish a connection to Twitter.',
        
        'error_favorite_on': '<b>%s</b> Tweet couldn\'t be favorited.',
        'error_favorite_off': '<b>%s</b> Tweet couldn\'t be unfavorited.',
        
        'error_ratelimit_reconnect':
             'Twitters limit on requests has been exceeded.\n'
             'Automatic reconnect in %d minute(s).',
        
        # Error Button stuff
        'error_button_twitter': 'Twitter server error',
        'error_twitter': 'The Twitter server did not respond to the request.',
        
        'error_button_down': 'Twitter is offline',
        'error_down':
            'Could not establish a connection to the Twitter server.',
        
        'error_button_rate_limit': 'Ratelimit exceeded',
        'error_rate_limit':
            'Twitters limit on requests has been exceeded.\n'
            'Automatic refresh in %d minute(s).',
        
        'error_template': '<b>Error from %H:%M:%S</b>\n',
        
        # Warning Dialogs
        'warning_title': 'Atarashii - Warning',
        
        'warning_button_rate_limit': 'Rate limit reduced',
        'warning_rate_limit':
            'Twitter has lowered the rate limit to %d requests per '
            'hour, the update interval has been adjusted accordingly.',
        
        'warning_button_overload': 'Twitter is over capacity',
        'warning_overload':
            'Twitter is currently over capacity, in most cases '
            'this is just a temporary issue and should fix itself in a '
            'couple of minutes.',
        
        'warning_button_network': 'Network error',
        'warning_network':
            'Atarashii couldn\'t establish a connection to the Internet.',
        
        'warning_network_timeout':
            'Atarashii has lost the conntection to Twitter, in most cases '
            'this is just a temporary issue due to Twitter being too '
            'busy at the moment.',
        
        'warning_network_twitter':
            'Atarashii couldn\'t establish a connection to Twitter.',
        
        'warning_template': '<b>Warning from %H:%M:%S</b>\n',
        
        # Info Button
        'info_title': '',
        'info_template': '',
        
        # Buttons
        'button_open': 'Click for more information',
        'button_remove': 'Click to remove',
        
        # Multibutton
        'multi_refresh': 'Refresh Tweets',
        'multi_history': 'Reset History',
        'multi_read': 'Mark all Tweets as read',
        'multi_refresh_message': 'Refresh Message',
        'multi_history_message': 'Remove History',
        'multi_read_message': 'Mark all Messages as read',
        
        # Tray Menu
        'menu_update': '_Refresh',
        'menu_read': '_Mark all as read',
        'menu_settings': '_Preferences',
        'menu_about': 'About',
        'menu_accounts': '_Accounts',
        'menu_logout': 'L_ogout',
        'menu_quit': '_Quit',
        
        # Tray Tooltip
        'tray_title': 'Atarashii',
        'tray_logging_in': 'Connecting as <b>%s</b>...',
        'tray_logged_out': 'Not connected.',
        'tray_logged_in': 'Logged in as <b>%s</b>.',
        
        'tray_tweet': '<b>%d</b> unread Tweet',
        'tray_message': '<b>%d</b> unread Message',
        'tray_tweets': '<b>%d</b> unread Tweets',
        'tray_messages': '<b>%d</b> unread Messages',
        
        # These are shown in the notifications, tags get removed
        'tray_error_login': 'Login as <b>%s</b> failed.',
        'tray_error_rate': 'Request limit exceeded.',
        'tray_warning_network': '<b>Network error.</b>',
        'tray_warning_overload': '<b>Twitter is over capacity.</b>',
        'tray_warning_timeout': '<b>Network error.</b>',
        'tray_warning_twitter': '<b>Twitter is unavailable.</b>',
        'tray_error_twitter': 'Twitter server error.',
        'tray_error_down': 'Twitter is offline.',
        'tray_error_rate_limit': 'Ratelimit exceeded.',
        
        # Context Menu
        'content_block': 'Block %s',
        'content_unfollow': 'Unfollow %s',
        'context_browser': 'Open in _Browser',
        'context_copy': '_Copy link location',
        'context_copy_tweet': '_Copy Tweet',
        'context_copy_message': '_Copy Message',
        'context_copy_tag': '_Copy Hashtag',
        'context_profile': 'Visit %s on Twitter.com',
        'context_reply': '_Reply to %s...',
        'context_tweet': '_Tweet to %s...',
        'context_message': '_Message to %s...',
        'context_source': '%s _Homepage',
        'context_view': 'View on Twitter.com',
        'context_search': 'Search on Twitter.com',
        'context_retweet_old': 'Retweet %s via _RT',
        'context_retweet_new': 'Retweet %s via _Twitter',
        'context_delete_tweet': '_Delete Tweet',
        'context_delete_message': '_Delete Message',
        'context_edit_tweet': '_Edit Tweet',
        'context_friend_loading': 'Retrieving status...',
        'context_friend_follow': 'Follow %s',
        'context_friend_unfollow': 'Unfollow %s',
        'context_friend_block': 'Block %s',
        'context_friend_unblock': 'Unblock %s'
    }
}

# Select Language
LANG_NAME = locale.getdefaultlocale()[0][0:2]
LANG = Language(LANG_NAME)

