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


# English ----------------------------------------------------------------------
# ------------------------------------------------------------------------------
LANG = {
    
    # Title
    'title': 'Atarashii',
    'title_logged_in': '%s - Atarashii',
    'title_logging_in': 'Connecting as %s...',
    
    # Tabs
    'tabs_tweets': 'Tweets',
    'tabs_tweets_new': 'Tweets <b>(%d)</b>',
    'tabs_messages': 'Messages',
    'tabs_messages_new': 'Messages <b>(%d)</b>',
    
    # Name endings
    'name_end': '\'s',
    'name_end_xzs': '\'s',
    
    # Tweets
    'tweet_hash': '#', # you may use the unicode fullwidth version here
    'tweet_at': '@', # you may use the unicode fullwidth version here
    
    # HTML
    'html_welcome': 'Welcome to Atarashii.',
    'html_loading': 'Loading Tweets...',
    
    'html_login_failed':
        'Login as %s failed.',
    
    'html_login_failed_info':
        'Either Twitter is currently not available, or you have used an '
        'invalid Username and/or Password.',
    
    'html_login_failed_button': 'Try again',
    
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
    'html_favorite': 'Favorite this Tweet',
    'html_unfavorite': 'Un-favorite this Tweet',
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
    'profile_follows_you': '(<b>including you</b>)',
    'profile_protected': '(<b>protected</b>)',
    
    'profile_error':
        'Could not load <b>%s</b> profile, the user does not exist.',
    
    'profile_warning':
        'Could not load <b>%s</b> profile, Twitter is currently unavailable.',
    
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
    'profile_html_tweet_error': 'Tweets could not be loaded.',
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
    
    # Progress bar
    'progress_syncing': 'Sychronization',
    'progress_login': 'Login to Twitter',
    'progress_tweets': 'Loading Tweets',
    'progress_messages': 'Loading Messages',
    
    'progress_user': 'Retrieving user',
    'progress_status': 'Requesting status',
    
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
    'settings_button_cancel': 'Cancel',
    'settings_tab_general': 'General',
    'settings_tab_accounts': 'Accounts',
    'settings_tab_notifications': 'Notifications',
    'settings_tab_theme': 'Theme',
    'settings_tab_atarashii': 'Atarashii',
    'settings_tab_syncing': 'Synchronization',
    
    'settings_add': 'Add',
    'settings_edit': 'Edit',
    'settings_delete': 'Delete',
    'settings_account_name': 'Name',
    'settings_account_tweets': 'Tweets',
    'settings_account_follower': 'Followers',
    'settings_account_friends': 'Following',
    
    'settings_autostart': 'Start on system startup',
    'settings_tray': 'Start minimized',
    'settings_taskbar': 'Show in Taskbar',
    'settings_info_sound': 'Activate info sounds',
    'settings_shortener': 'URL-Shortener:',
    'settings_shortener_off': 'Deactivated',
    'settings_continue': 'Cont. character:',
    'settings_continue_names': ['Points', 'Hyphen', 'Tilde', 'Arrow'],
    
    'settings_avatar_size': 'Avatar size:',
    'settings_font_size': 'Font size:',
    'settings_color_theme': 'Color scheme:',
    
    'settings_notifications_enable': 'Enable notifications',
    'settings_notifications_network': 'Notify on network errors',
    'settings_notifications_overlay': 'Overlay playing movies',
    'settings_notifications_sound': 'Activate sounds',
    'settings_file_tweets': 'Tweets:',
    'settings_file_replies': 'Replies:',
    'settings_file_messages': 'Messages:',
    'settings_file_info': 'Other:',
    'settings_file': 'Select soundfile',
    'settings_file_none': '...',
    'settings_file_filter': 'Soundfiles',
    'settings_file_ok': 'OK',
    'settings_file_cancel': 'Cancel',
    
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
        'haven\'t been used in the first <b>24 hours</b> after their '
        'generation.',
    
    'sync_user_error_title': 'Invalid Token',
    'sync_user_error':
        'No synchronization data for the entered Sync-Token was found, '
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
        'Do you want to report <b>%s</b> for Spam/Abuse?',
    
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
    
    'error_favorite_on': '<b>%s</b> Tweet couldn\'t be favored.',
    'error_favorite_off': '<b>%s</b> Tweet couldn\'t be unfavored.',
    
    'error_ratelimit_reconnect':
         'Twitters limit on requests has been exceeded.\n'
         'Automatic reconnect in %d minute(s).',
    
    # Error Button stuff
    'error_button_twitter': 'Twitter server error',
    'error_twitter': 'The Twitter server did not respond to the request.',
    
    'error_button_down': 'Twitter is offline',
    'error_down':
        'Could not establish a connection to the Twitter server.',
    
    'error_button_rate_limit': 'Rate limit exceeded',
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
        'Atarashii has lost the connection to Twitter, in most cases '
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
    'menu_update': '_Refresh all',
    'menu_read': '_Mark all as read',
    'menu_settings': '_Preferences',
    'menu_about': 'About',
    'menu_accounts': '_Accounts',
    'menu_logout': 'L_og out',
    'menu_secure_logout': 'Secure logout',
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
    
    # These are shown in the tray tooltip and the notifications
    # (tags get removed in the notifications)
    'tray_error_login': 'Login as <b>%s</b> failed.',
    'tray_error_rate': 'Request limit exceeded.',
    'tray_warning_network': '<b>Network error.</b>',
    'tray_warning_overload': '<b>Twitter is over capacity.</b>',
    'tray_warning_timeout': '<b>Network error.</b>',
    'tray_warning_twitter': '<b>Twitter is unavailable.</b>',
    'tray_error_twitter': 'Twitter server error.',
    'tray_error_down': 'Twitter is offline.',
    'tray_error_rate_limit': 'Rate limit exceeded.',
    
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

