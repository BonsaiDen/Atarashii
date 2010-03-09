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


# Language Settings ------------------------------------------------------------
# ------------------------------------------------------------------------------
import locale

class LangDE:
	def __init__(self):
		# Title
		self.title = "Atarashii"
		self.titleLoggedIn = "%s - Atarashii"
	
		# HTML
		self.htmlWelcome = "Willkommen bei Atarashii!"
		self.htmlLoading = "Tweets werden geladen..."
		self.htmlInfo = "Name: %s\nFollower: %d\nFollowing: %d\nTweets: %d"
		self.htmlProfile = "%s auf Twitter.com"
		self.htmlAt = "%s auf Twitter.com"
		self.htmlReply = "%s antworten"
		self.htmlRetweet = "%s retweeten"
		self.htmlTime = "Getwittert um %H:%M:%S Uhr"
		self.htmlTimeDay = "Getwittert am %d.%m.%Y um %H:%M:%S Uhr"
		self.htmlSearch = "Suche nach &quot;%s&quot;"
		self.htmlBy = " von %s"
		self.htmlInReply = "in Antwort auf %s"
		self.htmlInRetweet = "retweeted von %s"
		self.htmlLoadMore = "Mehr"
		self.htmlEmpty = "Keine Tweets"
		self.htmlProtected = "%s's Tweets sind geschützt"
		
		self.htmlAboutSecond = 'vor circa einer Sekunde'
		self.htmlSecond = 'vor %d Sekunden'
		self.htmlAboutMinute = 'vor circa einer Minute'
		self.htmlMinute = 'vor %d Minuten'
		self.htmlAboutHour = 'vor circa einer Stunde'
		self.htmlHour = 'vor %d Stunden'
		self.htmlAboutDay = 'vor circa einem Tag'
		self.htmlDay = 'vor %d Tagen'
		self.htmlYesterday = "von Gestern"
		self.htmlExact = "vom %d.%m.%Y"
		
		# Messages
		self.messageLoading = "Nachrichten werden geladen..."
		self.messageLoadMore = "Mehr"
		self.messageEmpty = "Keine Nachrichten"
		self.messageFrom = "Von"
		self.messageTo = "An"
		
		# Notifications
		self.notificationMessage = "Nachricht von %s"
		self.notificationIndex = "%s (%d von %d)"
		
		# Text
		self.textEntry = "Was passiert gerade?"
		self.textEntryMessage = "Nachricht eingeben..."
		
		# Status
		self.statusLogout = "Nicht verbunden."
		self.statusConnecting = "Verbinde als %s..."
		self.statusConnected = "Verbunden, aktualisiere..."
		self.statusError = "Verbindung fehlgeschlagen."
		self.statusSeconds = "Aktualisierung in %s Sekunden."
		self.statusOneSecond = "Aktualisierung in einer Sekunde."
		self.statusMinute = "Aktualisierung in einer Minute."
		self.statusMinutes = "Aktualisierung in %d Minuten."
		
		self.statusUpdate = "Aktualisiere..."
		self.statusReply = "Antworte %s..."
		self.statusRetweet = "Retweete %s..."
		self.statusMessage = "Sende Nachricht an %s..."
		self.statusMessageReply = "Antworte %s..."
		self.statusSend = "Sende Status..."
		self.statusLeft = "Noch %d Zeichen."
		self.statusMore = "%d Zeichen zu viel."
		self.statusLoadHistory = "Tweets werden geladen..."
		self.statusLoadMessageHistory = "Nachrichten werden geladen..."
		
		self.statusReconnectSeconds = "Automatischer Reconnect in %d Sekunden."
		self.statusReconnectMinute = "Automatischer Reconnect in einer Minute."
		self.statusReconnectMinutes = "Automatischer Reconnect in %d Minuten."
		
		# Reply
		self.labelReply = "<b>Antwort an %s:</b>"
		self.labelReplyText = "<b>Antwort auf:</b> %s"
		self.labelRetweet = "<b>%s retweeten:</b>"
		self.labelMessage = "<b>Nachricht an %s:</b>"
		self.labelMessageText = "<b>Antwort auf:</b> %s"
		
		# Settings
		self.settingsTitle = "Atarashii - Einstellungen"
		self.settingsButton = "Speichern"
		self.settingsButtonCancel = "Abbrechen"
		self.settingsAccounts = "Benutzer"
		self.settingsNotifications = "Benachrichtigungen"
		self.settingsNotify = "Aktivieren"
		self.settingsSound = "Sound abspielen"
		self.settingsFile = "Sounddatei"
		self.settingsFileFilter = "Soundateien"
		
		self.settingsRetweets = "Retweets"
		self.settingsRetweetsAsk = "Immer fragen"
		self.settingsRetweetsNew = "Immer neue Retweets verwenden"
		self.settingsRetweetsOld = "Immer alte Retweets verwenden"
		
		self.settingsAdd = "Erstellen"
		self.settingsEdit = "Bearbeiten"
		self.settingsDelete = "Löschen"
		
		# About
		self.aboutTitle = "Über Atarashii"
		self.aboutLicenseButton = "Lizenz"
		self.aboutOKButton = "OK"
		
		# Account
		self.accountEdit = "Benutzer bearbeiten"
		self.accountCreate = "Benutzer erstellen"
		self.accountDelete = "Benutzer löschen"
		self.accountDeleteDescription = 'Möchten sie den Benutzer "%s" wirklich löschen?'
		self.accountButton = "OK"
		self.accountButtonCancel = "Abbrechen"
		self.accountUsername = "Benutzername:"
		
		# Password
		self.passwordButton = "OK"
		self.passwordButtonCancel = "Abbrechen"
		self.passwordTitle = "Passwort"
		self.passwordQuestion = "%s's Passwort:"
		
		# Retweet
		self.retweetTitle = "%s retweeten"
		self.retweetQuestion = "Möchten sie einen neuen Retweet verwenden?"
		self.retweetInfoTitle = "Retweet erfolgreich"
		self.retweetInfo = '"%s" wurde erfolgreich retweeted!'
		
		# Error
		self.errorTitle = "Atarashii - Fehler"
 		self.errorLogin = 'Die Anmeldung als "%s" ist fehlgeschlagen.'
 		self.errorRatelimit = "Ratelimit erreicht. Automatische Aktualisierung in %d Minute(n)."
 		self.errorRatelimitReconnect = "Ratelimit erreicht. Automatischer Reconnect in %d Minute(n)."
 		self.errorTwitter = "Interner Twitterfehler."
 		self.errorDown = "Twitter ist gerade offline."
 		self.errorOverload = "Twitter ist gerade überlastet."
 		self.errorInternal = "Atarashii Fehler: %s"
 		self.errorAlreadyRetweeted = "Es ist entweder nicht möglich diesen Tweet zu retweeten oder er wurde bereits von ihnen retweeted."

		# Warning
		self.warningTitle = "Atarashii - Warnung"
		self.warningText = "Twitter hat das Ratelimit auf %d Requests pro Stunde reduziert, das Updateinterval wurde entsprechend angepasst."
 		self.warningURL = "Atarashii konnte Twitter nicht erreichen, dies ist in den meisten Fällen lediglich ein temporäres Problem aufgrund von Überlastung seitens Twitter."
		
		# Menu
		self.menuUpdate = "Aktualisieren"
		self.menuSettings = "Einstellungen"
		self.menuAbout = "Über Atarashii"
		self.menuQuit = "Beenden"
		
		# Toolbar
		self.toolRefresh = "Tweets aktualisieren"
		self.toolHistory = "Ältere Tweets entfernen"
		self.toolRead = "Alle Tweets als gelesen markieren"
		self.toolMode = "Nachrichten"
		self.toolSettings = "Einstellungen öffnen"
		self.toolAbout = "Einige Informationen über Atarashii"
		self.toolQuit = "Atarashii beenden"
		
		self.toolRefreshMessage = "Nachrichten aktualisieren"
		self.toolHistoryMessage = "Ältere Nachrichten entfernen"
		self.toolReadMessage = "Alle Nachrichten als gelesen markieren"
	
		# Title
		self.titleMessage = "%d neue Nachricht"
		self.titleMessages = "%d neue Nachrichten"
		
		self.titleTweet = "%d neuer Tweet"
		self.titleTweets = "%d neue Tweets"
			

class LangEN:
	def __init__(self):
		# Title
		self.title = "Atarashii"
		self.titleLoggedIn = "%s - Atarashii"
	
		# HTML
		self.htmlWelcome = "Welcome to Atarashii!"
		self.htmlLoading = "Loading Tweets..."
		self.htmlInfo = "Name: %s\nFollower: %d\nFollowing: %d\nTweets: %d"
		self.htmlProfile = "%s at Twitter.com"
		self.htmlAt = "%s at Twitter.com"
		self.htmlReply = "Reply to %s"
		self.htmlRetweet = "Retweet %s"
		self.htmlTime = "Tweeted at %H:%M:%S"
		self.htmlTimeDay = "Tweeted on %m.%d.%Y at %H:%M:%S"
		self.htmlSearch = "Search for &quot;%s&quot;"
		self.htmlBy = " by %s"
		self.htmlInReply = "in reply to %s"
		self.htmlInRetweet = "retweeted by %s"
		self.htmlLoadMore = "More"
		self.htmlEmpty = "No Tweets"
		self.htmlProtected = "%s's Tweets are protected"
		
		self.htmlAboutSecond = 'about one second ago'
		self.htmlSecond = '%d seconds ago'
		self.htmlAboutMinute = 'about a minute ago'
		self.htmlMinute = '%d minutes ago'
		self.htmlAboutHour = 'about an hour ago'
		self.htmlHour = '%d hours ago'
		self.htmlAboutDay = 'about a day ago'
		self.htmlDay = '%d days ago'
		self.htmlYesterday = "from yesterday"
		self.htmlExact = "from %m.%d.%Y"
		
		# Messages
		self.messageLoading = "Loading messages..."
		self.messageLoadMore = "More"
		self.messageEmpty = "No Messages"
		self.messageFrom = "From"
		self.messageTo = "To"
		
		# Notifications
		self.notificationMessage = "Message from %s:"
		self.notificationMessage = "Message from %s"
		self.notificationIndex = "%s (%d of %d)"
		
		
		# Text
		self.textEntry = "What's happening?"
		self.textEntryMessage = "Enter Message..."
		
		# Status
		self.statusLogout = "Not connected."
		self.statusConnecting = "Connecting as %s..."
		self.statusConnected = "Connected, loading..."
		self.statusError = "Connection failed."
		self.statusSeconds = "Refresh in %s seconds."
		self.statusOneSecond = "Refresh in one second."
		self.statusMinute = "Refresh in one minute."
		self.statusMinutes = "Refresh in %d minutes."
		
		self.statusUpdate = "Sending Status..."
		self.statusReply = "Replying to %s..."
		self.statusRetweet = "Retweeting %s..."
		self.statusMessage = "Sending Message to %s..."
		self.statusMessageReply = "Replying to %s..."
		self.statusSend = "Sending Status..."
		self.statusLeft = "%d chars left."
		self.statusMore = "%d chars too much."
		self.statusLoadHistory = "Loading Tweets..."
		self.statusLoadMessageHistory = "Loading Messages..."
		
		self.statusReconnectSeconds = "Automatic reconnect in %d seconds."
		self.statusReconnectMinute = "Automatic reconnect in one minute."
		self.statusReconnectMinutes = "Automatic reconnect in %d minutes."
			
		
		# Reply
		self.labelReply = "<b>Reply to %s:</b>"
		self.labelReplyText = "<b>Reply on:</b> %s"
		self.labelRetweet = "<b>Retweet %s:</b>"
		self.labelMessage = "<b>Message to %s:</b>"
		self.labelMessageText = "<b>Message on:</b> %s"
		
		# Settings
		self.settingsTitle = "Atarashii - Preferences"
		self.settingsButton = "Save"
		self.settingsButtonCancel = "Cancel"
		self.settingsAccounts = "Users"
		self.settingsNotifications = "Notifications"
		self.settingsNotify = "Enable"
		self.settingsSound = "Play sound"
		self.settingsFile = "Soundfile"
		self.settingsFileFilter = "Soundfiles"
		
		self.settingsRetweets = "Retweets"
		self.settingsRetweetsAsk = "Always ask which style to use"
		self.settingsRetweetsNew = "Always use new style"
		self.settingsRetweetsOld = "Always use old style"
		
		self.settingsAdd = "Add"
		self.settingsEdit = "Edit"
		self.settingsDelete = "Delete"
		
		# About
		self.aboutTitle = "About Atarashii"
		self.aboutLicenseButton = "License"
		self.aboutOKButton = "OK"
		
		# Account
		self.accountEdit = "Edit user"
		self.accountCreate = "Create a new user"
		self.accountDelete = "Delete user"
		self.accountDeleteDescription = 'Do you really want to delete the user "%s"?'
		self.accountButton = "OK"
		self.accountButtonCancel = "Cancel"
		self.accountUsername = "Username:"
		
		# Password
		self.passwordButton = "OK"
		self.passwordButtonCancel = "Cancel"
		self.passwordTitle = "Password"
		self.passwordQuestion = "%s's password:"
		
		# Retweet
		self.retweetTitle = "Retweet %s"
		self.retweetQuestion = "Do you want to use a new style Retweet?"
		self.retweetInfoTitle = "Retweet successful"
		self.retweetInfo = '"%s" has been successfully retweeted!'
		
		# Error
		self.errorTitle = "Atarashii - Error"
 		self.errorLogin = 'The login as "%s" has failed.'
 		self.errorRatelimit = "Reached rate limit. Automatic refresh in %d minute(s)."
 		self.errorRatelimitReconnect = "Reached rate limit. Automatic reconnect in %d minute(s)."
 		
 		self.errorTwitter = "Internal Twitter error."
 		self.errorDown = "Twitter is currently offline."
 		self.errorOverload = "Twitter is over capacity."
 		self.errorInternal = "Atarashii error: %s"
 		self.errorAlreadyRetweeted = "Either it's not possible to retweet this Tweet or you've already retweeted it."
		
		# Warning
		self.warningTitle = "Atarashii - Warning"
		self.warningText = "Twitter has lowered the rate limit to %d requests per hour, the update interval has been adjusted accordingly."
 		self.warningURL = "Atarashii couldn't connect to Twitter, in most cases this is just a temporary issue due to Twitter being too busy at the moment."
		
		# Toolbar
		self.toolRefresh = "Refresh Tweets"
		self.toolHistory = "Remove History"
		self.toolRead = "Mark all Tweets as read"
		self.toolMode = "Messages"
		self.toolSettings = "Open Preferences"
		self.toolAbout = "Some information about Atarashii"
		self.toolQuit = "Quit Atarashii"
		
		self.toolRefreshMessage = "Refresh Message"
		self.toolHistoryMessage = "Remove History"
		self.toolReadMessage = "Mark all Messages as read"
		
		# Menu
		self.menuUpdate = "Refresh"
		self.menuSettings = "Preferences"
		self.menuAbout = "About Atarashii"
		self.menuQuit = "Quit"
		
		# Title
		self.titleMessage = "%d new Message"
		self.titleMessages = "%d new Messages"
		
		self.titleTweet = "%d new Tweet"
		self.titleTweets = "%d new Tweets"	


# Select Language
langs = {
	"de_DE" : LangDE,
	"en_US" : LangEN
}

lo = locale.getdefaultlocale()[0]
if langs.has_key(lo):
	lang = langs[lo]()
else:
	lang = langs["en_US"]()

