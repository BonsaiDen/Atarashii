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
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
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
		'titleLoggedIn' : '%s - Atarashii',
		'titleMessage' : '%d neue Nachricht',
		'titleMessages' : '%d neue Nachrichten',
		'titleTweet' : '%d neuer Tweet',
		'titleTweets' : '%d neue Tweets',
	
		# HTML
		'htmlWelcome' : 'Willkommen bei Atarashii!',
		'htmlLoading' : 'Tweets werden geladen...',
		'htmlInfo' : 'Name: %s\nFollower: %d\nFollowing: %d\nTweets: %d',
		'htmlProfile' : '%s auf Twitter.com',
		'htmlAt' : '%s auf Twitter.com',
		'htmlReply' : '%s antworten',
		'htmlRetweet' : '%s retweeten',
		'htmlTime' : 'Getwittert um %H:%M:%S Uhr',
		'htmlTimeDay' : 'Getwittert am %d.%m.%Y um %H:%M:%S Uhr',
		'htmlSearch' : 'Suche nach &quot;%s&quot;',
		'htmlBy' : ' von %s',
		'htmlInReply' : 'in Antwort auf %s',
		'htmlInRetweet' : 'retweeted von %s',
		'htmlLoadMore' : 'Mehr',
		'htmlEmpty' : 'Keine Tweets',
		'htmlProtected' : '%s\'s Tweets sind geschützt',
		'htmlAboutSecond' : 'vor circa einer Sekunde',
		'htmlSecond' : 'vor %d Sekunden',
		'htmlAboutMinute' : 'vor circa einer Minute',
		'htmlMinute' : 'vor %d Minuten',
		'htmlAboutHour' : 'vor circa einer Stunde',
		'htmlHour' : 'vor %d Stunden',
		'htmlAboutDay' : 'vor circa einem Tag',
		'htmlDay' : 'vor %d Tagen',
		'htmlYesterday' : 'von Gestern',
		'htmlExact' : 'vom %d.%m.%Y',
	
		# Messages
		'messageLoading' : 'Nachrichten werden geladen...',
		'messageLoadMore' : 'Mehr',
		'messageEmpty' : 'Keine Nachrichten',
		'messageFrom' : 'Von',
		'messageTo' : 'An',
	
		# Notifications
		'notificationMessage' : 'Nachricht von %s',
		'notificationIndex' : '%s (%d von %d)',
	
		# Textbox
		'textEntry' : 'Was passiert gerade?',
		'textEntryMessage' : 'Nachricht eingeben...',
	
		# Statusbar
		'statusLogout' : 'Nicht verbunden.',
		'statusConnecting' : 'Verbinde als %s...',
		'statusConnected' : 'Verbunden, aktualisiere...',
		'statusError' : 'Verbindung fehlgeschlagen.',
		'statusSeconds' : 'Aktualisierung in %s Sekunden.',
		'statusOneSecond' : 'Aktualisierung in einer Sekunde.',
		'statusMinute' : 'Aktualisierung in einer Minute.',
		'statusMinutes' : 'Aktualisierung in %d Minuten.',
		'statusUpdate' : 'Aktualisiere...',
		'statusReply' : 'Antworte %s...',
		'statusRetweet' : 'Retweete %s...',
		'statusMessage' : 'Sende Nachricht an %s...',
		'statusMessageReply' : 'Antworte %s...',
		'statusSend' : 'Sende Status...',
		'statusLeft' : 'Noch %d Zeichen.',
		'statusMore' : '%d Zeichen zu viel.',
		'statusLoadHistory' : 'Tweets werden geladen...',
		'statusLoadMessageHistory' : 'Nachrichten werden geladen...',
		'statusReconnectSeconds' : 'Automatischer Reconnect in %d Sekunden.',
		'statusReconnectMinute' : 'Automatischer Reconnect in einer Minute.',
		'statusReconnectMinutes' : 'Automatischer Reconnect in %d Minuten.',
	
		# Info Label
		'labelReply' : '<b>Antwort an %s:</b>',
		'labelReplyText' : '<b>Antwort auf:</b> %s',
		'labelRetweet' : '<b>%s retweeten:</b>',
		'labelMessage' : '<b>Nachricht an %s:</b>',
		'labelMessageText' : '<b>Antwort auf:</b> %s',
	
		# Settings Dialog
		'settingsTitle' : 'Atarashii - Einstellungen',
		'settingsButton' : 'Speichern',
		'settingsButtonCancel' : 'Abbrechen',
		'settingsAccounts' : 'Benutzer',
		'settingsNotifications' : 'Benachrichtigungen',
		'settingsNotify' : 'Aktivieren',
		'settingsSound' : 'Sound abspielen',
		'settingsFile' : 'Sounddatei',
		'settingsFileFilter' : 'Soundateien',
		'settingsRetweets' : 'Retweets',
		'settingsRetweetsAsk' : 'Immer fragen',
		'settingsRetweetsNew' : 'Immer neue Retweets verwenden',
		'settingsRetweetsOld' : 'Immer alte Retweets verwenden',
		'settingsAdd' : 'Erstellen',
		'settingsEdit' : 'Bearbeiten',
		'settingsDelete' : 'Löschen',
	
		# About Dialog
		'aboutTitle' : 'Über Atarashii',
		'aboutLicenseButton' : 'Lizenz',
		'aboutOKButton' : 'OK',
	
		# Account Dialog
		'accountEdit' : 'Benutzer bearbeiten',
		'accountCreate' : 'Benutzer erstellen',
		'accountDelete' : 'Benutzer löschen',
		'accountDeleteDescription' : 'Möchten sie den Benutzer "%s" wirklich löschen?',
		'accountButton' : 'OK',
		'accountButtonCancel' : 'Abbrechen',
		'accountUsername' : 'Benutzername:',
	
		# Password Dialog
		'passwordButton' : 'OK',
		'passwordButtonCancel' : 'Abbrechen',
		'passwordTitle' : 'Passwort',
		'passwordQuestion' : '%s\'s Passwort:',
	
		# Retweet Dialogs
		'retweetTitle' : '%s retweeten',
		'retweetQuestion' : 'Möchten sie einen neuen Retweet verwenden?',
		'retweetInfoTitle' : 'Retweet erfolgreich',
		'retweetInfo' : '"%s" wurde erfolgreich retweeted!',
	
		# Error Dialogs
		'errorTitle' : 'Atarashii - Fehler',
		'errorLogin' : 'Die Anmeldung als "%s" ist fehlgeschlagen.',
		'errorRatelimit' : 'Ratelimit erreicht. Automatische Aktualisierung in %d Minute(n).',
		'errorRatelimitReconnect' : 'Ratelimit erreicht. Automatischer Reconnect in %d Minute(n).',
		'errorTwitter' : 'Interner Twitterfehler.',
		'errorDown' : 'Twitter ist gerade offline.',
		'errorOverload' : 'Twitter ist gerade überlastet.',
		'errorInternal' : 'Atarashii Fehler: %s',
		'errorAlreadyRetweeted' : 'Es ist entweder nicht möglich diesen Tweet zu retweeten oder er wurde bereits von ihnen retweeted.',
		'errorUserNotFound' : 'Der Benutzer "%s" existiert nicht.',
		
		# Warning Dialogs
		'warningTitle' : 'Atarashii - Warnung',
		'warningText' : 'Twitter hat das Ratelimit auf %d Requests pro Stunde reduziert, das Updateinterval wurde entsprechend angepasst.',
		'warningURL' : 'Atarashii konnte Twitter nicht erreichen, dies ist in den meisten Fällen lediglich ein temporäres Problem aufgrund von Überlastung seitens Twitter.',
	
		# Toolbar Items
		'toolRefresh' : 'Tweets aktualisieren',
		'toolHistory' : 'Ältere Tweets entfernen',
		'toolRead' : 'Alle Tweets als gelesen markieren',
		'toolMode' : 'Nachrichten',
		'toolSettings' : 'Einstellungen öffnen',
		'toolAbout' : 'Einige Informationen über Atarashii',
		'toolQuit' : 'Atarashii beenden',
		'toolRefreshMessage' : 'Nachrichten aktualisieren',
		'toolHistoryMessage' : 'Ältere Nachrichten entfernen',
		'toolReadMessage' : 'Alle Nachrichten als gelesen markieren',
	
		# Tray Menu
		'menuUpdate' : 'Aktualisieren',
		'menuSettings' : 'Einstellungen',
		'menuAbout' : 'Über Atarashii',
		'menuQuit' : 'Beenden'
	},


	# English ------------------------------------------------------------------
	# --------------------------------------------------------------------------
	'en_US' : {
		# Title
		'title' : 'Atarashii',
		'titleLoggedIn' : '%s - Atarashii',
		'titleMessage' : '%d new Message',
		'titleMessages' : '%d new Messages',
		'titleTweet' : '%d new Tweet',
		'titleTweets' : '%d new Tweets',
	
		# HTML
		'htmlWelcome' : 'Welcome to Atarashii!',
		'htmlLoading' : 'Loading Tweets...',
		'htmlInfo' : 'Name: %s\nFollower: %d\nFollowing: %d\nTweets: %d',
		'htmlProfile' : '%s at Twitter.com',
		'htmlAt' : '%s at Twitter.com',
		'htmlReply' : 'Reply to %s',
		'htmlRetweet' : 'Retweet %s',
		'htmlTime' : 'Tweeted at %H:%M:%S',
		'htmlTimeDay' : 'Tweeted on %m.%d.%Y at %H:%M:%S',
		'htmlSearch' : 'Search for &quot;%s&quot;',
		'htmlBy' : ' by %s',
		'htmlInReply' : 'in reply to %s',
		'htmlInRetweet' : 'retweeted by %s',
		'htmlLoadMore' : 'More',
		'htmlEmpty' : 'No Tweets',
		'htmlProtected' : '%s\'s Tweets are protected',
		'htmlAboutSecond' : 'about one second ago',
		'htmlSecond' : '%d seconds ago',
		'htmlAboutMinute' : 'about a minute ago',
		'htmlMinute' : '%d minutes ago',
		'htmlAboutHour' : 'about an hour ago',
		'htmlHour' : '%d hours ago',
		'htmlAboutDay' : 'about a day ago',
		'htmlDay' : '%d days ago',
		'htmlYesterday' : 'from yesterday',
		'htmlExact' : 'from %m.%d.%Y',
	
		# Messages
		'messageLoading' : 'Loading messages...',
		'messageLoadMore' : 'More',
		'messageEmpty' : 'No Messages',
		'messageFrom' : 'From',
		'messageTo' : 'To',
	
		# Notifications
		'notificationMessage' : 'Message from %s',
		'notificationIndex' : '%s (%d of %d)',
	
		# Textbox
		'textEntry' : 'What\'s happening?',
		'textEntryMessage' : 'Enter Message...',
	
		# Statusbar
		'statusLogout' : 'Not connected.',
		'statusConnecting' : 'Connecting as %s...',
		'statusConnected' : 'Connected, loading...',
		'statusError' : 'Connection failed.',
		'statusSeconds' : 'Refresh in %s seconds.',
		'statusOneSecond' : 'Refresh in one second.',
		'statusMinute' : 'Refresh in one minute.',
		'statusMinutes' : 'Refresh in %d minutes.',
		'statusUpdate' : 'Sending Status...',
		'statusReply' : 'Replying to %s...',
		'statusRetweet' : 'Retweeting %s...',
		'statusMessage' : 'Sending Message to %s...',
		'statusMessageReply' : 'Replying to %s...',
		'statusSend' : 'Sending Status...',
		'statusLeft' : '%d chars left.',
		'statusMore' : '%d chars too much.',
		'statusLoadHistory' : 'Loading Tweets...',
		'statusLoadMessageHistory' : 'Loading Messages...',
		'statusReconnectSeconds' : 'Automatic reconnect in %d seconds.',
		'statusReconnectMinute' : 'Automatic reconnect in one minute.',
		'statusReconnectMinutes' : 'Automatic reconnect in %d minutes.',
	
		# Info Label
		'labelReply' : '<b>Reply to %s:</b>',
		'labelReplyText' : '<b>Reply on:</b> %s',
		'labelRetweet' : '<b>Retweet %s:</b>',
		'labelMessage' : '<b>Message to %s:</b>',
		'labelMessageText' : '<b>Message on:</b> %s',
	
		# Settings Dialog
		'settingsTitle' : 'Atarashii - Preferences',
		'settingsButton' : 'Save',
		'settingsButtonCancel' : 'Cancel',
		'settingsAccounts' : 'Users',
		'settingsNotifications' : 'Notifications',
		'settingsNotify' : 'Enable',
		'settingsSound' : 'Play sound',
		'settingsFile' : 'Soundfile',
		'settingsFileFilter' : 'Soundfiles',
		'settingsRetweets' : 'Retweets',
		'settingsRetweetsAsk' : 'Always ask which style to use',
		'settingsRetweetsNew' : 'Always use new style',
		'settingsRetweetsOld' : 'Always use old style',
		'settingsAdd' : 'Add',
		'settingsEdit' : 'Edit',
		'settingsDelete' : 'Delete',
	
		# About Dialog
		'aboutTitle' : 'About Atarashii',
		'aboutLicenseButton' : 'License',
		'aboutOKButton' : 'OK',
	
		# Account Dialog
		'accountEdit' : 'Edit user',
		'accountCreate' : 'Create a new user',
		'accountDelete' : 'Delete user',
		'accountDeleteDescription' : 'Do you really want to delete the user "%s"?',
		'accountButton' : 'OK',
		'accountButtonCancel' : 'Cancel',
		'accountUsername' : 'Username:',
		'passwordButton' : 'OK',
		'passwordButtonCancel' : 'Cancel',
		'passwordTitle' : 'Password',
		'passwordQuestion' : '%s\'s password:',
	
		# Retweet Dialogs
		'retweetTitle' : 'Retweet %s',
		'retweetQuestion' : 'Do you want to use a new style Retweet?',
		'retweetInfoTitle' : 'Retweet successful',
		'retweetInfo' : '"%s" has been successfully retweeted!',
	
		# Error Dialogs
		'errorTitle' : 'Atarashii - Error',
		'errorLogin' : 'The login as "%s" has failed.',
		'errorRatelimit' : 'Reached rate limit. Automatic refresh in %d minute(s).',
		'errorRatelimitReconnect' : 'Reached rate limit. Automatic reconnect in %d minute(s).',
		'errorTwitter' : 'Internal Twitter error.',
		'errorDown' : 'Twitter is currently offline.',
		'errorOverload' : 'Twitter is over capacity.',
		'errorInternal' : 'Atarashii error: %s',
		'errorAlreadyRetweeted' : 'Either it\'s not possible to retweet this Tweet or you\'ve already retweeted it.',
		'errorUserNotFound' : 'The user "%s" does not exist.',
	
		# Warning Dialogs
		'warningTitle' : 'Atarashii - Warning',
		'warningText' : 'Twitter has lowered the rate limit to %d requests per hour, the update interval has been adjusted accordingly.',
		'warningURL' : 'Atarashii couldn\'t connect to Twitter, in most cases this is just a temporary issue due to Twitter being too busy at the moment.',
	
		# Toolbar items
		'toolRefresh' : 'Refresh Tweets',
		'toolHistory' : 'Remove History',
		'toolRead' : 'Mark all Tweets as read',
		'toolMode' : 'Messages',
		'toolSettings' : 'Open Preferences',
		'toolAbout' : 'Some information about Atarashii',
		'toolQuit' : 'Quit Atarashii',
		'toolRefreshMessage' : 'Refresh Message',
		'toolHistoryMessage' : 'Remove History',
		'toolReadMessage' : 'Mark all Messages as read',
	
		# Tray Menu
		'menuUpdate' : 'Refresh',
		'menuSettings' : 'Preferences',
		'menuAbout' : 'About Atarashii',
		'menuQuit' : 'Quit'
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


