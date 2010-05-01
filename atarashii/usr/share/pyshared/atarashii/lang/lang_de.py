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


# German -----------------------------------------------------------------------
# ------------------------------------------------------------------------------
LANG = {
    
    # Title
    'title': 'Atarashii',
    'title_logged_in': '%s - Atarashii',
    'title_logging_in': 'Verbinde als %s...',
    
    # Tabs
    'tabs_tweets': 'Tweets',
    'tabs_tweets_new': 'Tweets <b>(%d)</b>',
    'tabs_messages': 'Nachrichten',
    'tabs_messages_new': 'Nachrichten <b>(%d)</b>',
    
    # Name endings
    'name_end': 's',
    'name_end_xzs': '\'',
    
    # Tweets
    'tweet_hash': '#', # you may use the unicode fullwidth version here
    'tweet_at': '@', # you may use the unicode fullwidth version here
    
    # HTML
    'html_welcome': 'Willkommen bei Atarashii.',
    'html_loading': 'Tweets werden geladen...',
    
    'html_login_failed':
        'Anmeldung als %s fehlgeschlagen.',
    
    'html_login_failed_info':
        'Entweder ist Twitter derzeit nicht zu erreichen, oder Sie haben '
        'einen ungültigen Benutzernamen und/oder Passwort verwendet.',
    
    'html_login_failed_button': 'Erneut versuchen',
    
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
    'profile_close': '<b>%s</b> Profil schließen',
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
    'profile_html_empty': 'Keine aktuellen Tweets.',
    'profile_html_tweet_error': 'Tweets konnten nicht geladen werden.',
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
    'status_reconnect_seconds': 'Verbinde automatisch neu in %d Sekunden.',
    'status_reconnect_minute': 'Verbinde automatisch neu in einer Minute.',
    'status_reconnect_minutes': 'Verbinde automatisch neu in %d Minuten.',
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
    'settings_button_cancel': 'Abbrechen',
    'settings_tab_general': 'Allgemein',
    'settings_tab_accounts': 'Accounts',
    'settings_tab_notifications': 'Benachrichtigungen',
    'settings_tab_theme': 'Thema',
    'settings_tab_atarashii': 'Atarashii',
    'settings_tab_syncing': 'Synchronisation',
    
    'settings_add': 'Erstellen',
    'settings_edit': 'Bearbeiten',
    'settings_delete': 'Löschen',
    
    'settings_autostart': 'Automatisch starten',
    'settings_tray': 'Minimiert starten',
    'settings_taskbar': 'In der Taskleiste anzeigen',
    'settings_info_sound': 'Hinweissounds aktivieren',
    'settings_shortener': 'URL-Kürzer:',
    'settings_shortener_off': 'Deaktiviert',
    'settings_continue': 'Fortsetzungszeichen:',
    'settings_continue_names': ['Punkte', 'Strich', 'Tilde', 'Pfeil'],
    
    'settings_avatar_size': 'Avatargröße:',
    'settings_font_size': 'Schriftgröße:',
    'settings_color_theme': 'Farbschema:',
    
    'settings_notifications_enable': 'Benachrichtigungen aktivieren',
    'settings_notifications_overlay': 'Abspielende Filme überlagern',
    'settings_notifications_sound': 'Sounds aktivieren',
    'settings_file_tweets': 'Tweets:',
    'settings_file_replies': 'Antworten:',
    'settings_file_messages': 'Nachrichten:',
    'settings_file_info': 'Sonstige:',
    'settings_file': 'Sounddatei auswählen',
    'settings_file_none': '...',
    'settings_file_filter': 'Sounddateien',
    
    'settings_file_ok': 'OK',
    'settings_file_cancel': 'Abbrechen',
    
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
        'Es wurden keine Synchronisationsdaten für das eingegebene '
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
        'reduziert, das Aktualisierungsintervall wurde '
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
    'menu_update': 'Alles Aktualisie_ren',
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
    'content_unfollow': '%s unfollowen',
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
}

