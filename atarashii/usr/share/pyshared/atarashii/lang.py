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
		# HTML
		self.htmlWelcome = "Willkommen bei Atarashii!"
		self.htmlLoading = "Tweets werden geladen..."
		self.htmlInfo = "Name: %s\nFollower: %d\nFollowing: %d\nTweets: %d"
		self.htmlProfile = "%s Profil"
		self.htmlAt = "%s auf Twitter.com"
		self.htmlReply = "%s antworten"
		self.htmlRetweet = "%s retweeten"
		self.htmlTime = "Getwittert um %H:%M:%S Uhr"
		self.htmlTimeDay = "Getwittert am %d.%m.%Y um %H:%M:%S Uhr"
		self.htmlSearch = "Suche nach &quot;%s&quot;"
		self.htmlBy = " von %s"
		self.htmlInReply = "in Antwort auf %s"
		self.htmlLoadMore = "Mehr"
		self.htmlEmpty = "Keine Tweets"
		
		self.htmlAboutSecond = 'vor ungefähr einer Sekunde'
		self.htmlSecond = 'vor %d Sekunden'
		self.htmlAboutMinute = 'vor ungefähr einer Minute'
		self.htmlMinute = 'vor %d Minuten'
		self.htmlAboutHour = 'vor ungefähr einer Stunde'
		self.htmlHour = 'vor %d Stunden'
		self.htmlAboutDay = 'vor ungefähr einem Tag'
		self.htmlDay = 'vor %d Tagen'
		self.htmlYesterday = "von Gestern"
		self.htmlExact = "vom %d.%m.%Y"
		
		self.htmlHistory = "Ältere Tweets laden"
		self.htmlHistoryMessage = "Ältere Nachrichten laden"
		
		self.messageLoading = "Nachrichten werden geladen..."
		
		# Notifications
		self.notificationMessage = "Nachricht von %s:"
		
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
		self.statusSend = "Sende Tweet..."
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
		self.settingsTitle = "Einstellungen"
		self.settingsButton = "Speichern"
		self.settingsButtonCancel = "Abbrechen"
		self.settingsAccounts = "Benutzerkonten"
		self.settingsNotifications = "Benachrichtigungen"
		self.settingsNotify = "Aktivieren"
		self.settingsSound = "Sound abspielen"
		self.settingsFile = "Sounddatei"
		self.settingsFileFilter = "Soundateien"
		
		self.settingsAdd = "Erstellen"
		self.settingsEdit = "Bearbeiten"
		self.settingsDelete = "Löschen"
		
		# About
		self.aboutTitle = "Über Atarashii"
		self.aboutLicenseButton = "Lizenz"
		self.aboutOKButton = "OK"
		
		# Account
		self.accountEdit = "%s's Benutzerkonto bearbeiten"
		self.accountCreate = "Benutzerkonto erstellen"
		self.accountDelete = "%s's Benutzerkonto löschen"
		self.accountDeleteDescription = 'Möchten sie das Benutzerkonto von "%s" wirklich löschen?'
		self.accountButton = "OK"
		self.accountButtonCancel = "Abbrechen"
		self.accountUsername = "Benutzername:"
		self.accountPassword = "Passwort:"
		
		# Question
		self.questionButton = "Ja"
		self.questionButtonCancel = "Nein"
		
		# Error
		self.errorButton = "OK"
		self.errorTitle = "Fehler"
 		self.errorLogin = 'Die Anmeldung als "%s" ist fehlgeschlagen.'
 		self.errorRatelimit = "Ratelimit erreicht. Automatisches Update in %d Minute(n)."
 		self.errorRatelimitReconnect = "Ratelimit erreicht. Automatischer Reconnect in %d Minute(n)."
 		self.errorTwitter = "Interner Twitterfehler."
 		self.errorDown = "Twitter ist gerade offline."
 		self.errorOverload = "Twitter ist gerade überlastet."
 		self.errorInternal = "Atarashii Fehler: %s"
		
		# Warning
		self.warningButton = "OK"
		self.warningTitle = "Warnung"
		self.warningText = "Twitter hat das Ratelimit auf %d Requests pro Stunde reduziert, das Updateinterval wurde entsprechend angepasst."
		
		# Menu
		self.menuUpdate = "Aktualisieren"
		self.menuSettings = "Einstellungen"
		self.menuAbout = "Über Atarashii"
		self.menuQuit = "Beenden"
		
		# Toolbar
		self.toolRefresh = "Tweets aktualisieren"
		self.toolHistory = "Ältere Tweets entfernen"
		self.toolRead = "Alle Tweets als gelesen makieren"
		self.toolMode = "Nachrichten"
		self.toolSettings = "Einstellungen öffnen"
		self.toolAbout = "Einige Informationen über Atarashii"
		self.toolQuit = "Atarashii beenden"
		
		self.toolRefreshMessage = "Nachrichten aktualisieren"
		self.toolHistoryMessage = "Ältere Nachrichten entfernen"
		self.toolReadMessage = "Alle Nachrichten als gelesen makieren"

		# Tabs
		self.tabsTweets = "Tweets"
		self.tabsMessage = "Nachrichten"
		self.tabsTweetsNew = "Tweets<b>(%d)</b>"
		self.tabsMessageNew = "Nachrichten<b>(%d)</b>"
		self.tabsTweetsLoading = "Tweets..."
		self.tabsMessageLoading = "Nachrichten..."

class LangEN:
	def __init__(self):
		# HTML
		self.htmlWelcome = "Welcome to Atarashii!"
		self.htmlLoading = "Loading Tweets..."
		self.htmlInfo = "Name: %s\nFollower: %d\nFollowing: %d\nTweets: %d"
		self.htmlProfile = "%s profile"
		self.htmlAt = "%s on Twitter.com"
		self.htmlReply = "Reply to %s"
		self.htmlRetweet = "Retweet %s"
		self.htmlTime = "Tweeted at %H:%M:%S"
		self.htmlTimeDay = "Tweeted on %m.%d.%Y at %H:%M:%S"
		self.htmlSearch = "Search for &quot;%s&quot;"
		self.htmlBy = " by %s"
		self.htmlInReply = "in reply to %s"
		self.htmlLoadMore = "More"
		self.htmlEmpty = "No tweets."
		
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
		
		self.htmlHistory = "Load more tweets"
		self.htmlHistoryMessage = "Load more messages"
		
		self.messageLoading = "Loading messages..."
		
		# Notifications
		self.notificationMessage = "Message from %s:"
		
		# Text
		self.textEntry = "What's happening?"
		self.textEntryMessage = "Enter message..."
		
		# Status
		self.statusLogout = "Not connected."
		self.statusConnecting = "Connecting as %s..."
		self.statusConnected = "Connected, loading..."
		self.statusError = "Connection failed."
		self.statusSeconds = "Refresh in %s seconds."
		self.statusOneSecond = "Refresh in one second."
		self.statusMinute = "Refresh in one minute."
		self.statusMinutes = "Refresh in %d minutes."
		
		self.statusUpdate = "Sending tweet..."
		self.statusReply = "Replying to %s..."
		self.statusRetweet = "Retweeting %s..."
		self.statusMessage = "Sendind message to %s..."
		self.statusMessageReply = "Replying to %s..."
		self.statusSend = "Sending status..."
		self.statusLeft = "%d chars left."
		self.statusMore = "%d chars too much."
		self.statusLoadHistory = "Loading tweets..."
		self.statusLoadMessageHistory = "Loading messages..."
		
		self.statusReconnectSeconds = "Automatic reconnect in %d seconds."
		self.statusReconnectMinute = "Automatic reconnect in one minute."
		self.statusReconnectMinutes = "Automatic reconnect in %d minutes."
			
		
		# Reply
		self.labelReply = "<b>Reply to %s:</b>"
		self.labelReplyText = "<b>Reply on:</b> %s"
		self.labelRetweet = "<b>Rewteet %s:</b>"
		self.labelMessage = "<b>Message to %s:</b>"
		self.labelMessageText = "<b>Message on:</b> %s"
		
		# Settings
		self.settingsTitle = "Preferences"
		self.settingsButton = "Save"
		self.settingsButtonCancel = "Cancel"
		self.settingsAccounts = "Accounts"
		self.settingsNotifications = "Notifications"
		self.settingsNotify = "Enable"
		self.settingsSound = "Play sound"
		self.settingsFile = "Soundfile"
		self.settingsFileFilter = "Soundfiles"
		
		self.settingsAdd = "Add"
		self.settingsEdit = "Edit"
		self.settingsDelete = "Delete"
		
		# About
		self.aboutTitle = "About Atarashii"
		self.aboutLicenseButton = "License"
		self.aboutOKButton = "OK"
		
		# Account
		self.accountEdit = "Edit %s's account"
		self.accountCreate = "Create a new account"
		self.accountDelete = "Delete %s's account"
		self.accountDeleteDescription = 'Do you really want to delete the account "%s"?'
		self.accountButton = "OK"
		self.accountButtonCancel = "Cancel"
		
		self.accountUsername = "Username:"
		self.accountPassword = "Password:"
		
		# Question
		self.questionButton = "Yes"
		self.questionButtonCancel = "No"
		
		
		# Error
		self.errorButton = "OK"
		self.errorTitle = "Error"
 		self.errorLogin = 'The login as "%s" has failed.'
 		self.errorRatelimit = "Reached ratelimit. Automatic update in %d minute(s)."
 		self.errorRatelimitReconnect = "Reached ratelimit. Automatic reconnect in %d minute(s)."
 		
 		self.errorTwitter = "Internal Twitter error."
 		self.errorDown = "Twitter is currently offline."
 		self.errorOverload = "Twitter is over capacity."
 		self.errorInternal = "Atarashii error: %s"
		
		# Warning
		self.warningButton = "OK"
		self.warningTitle = "Warnung"
		self.warningText = "Twitter has lowered the ratelimit to %d requests per hour, the update interval has been adjusted accordingly."
		
		# Toolbar
		self.toolRefresh = "Refresh tweets"
		self.toolHistory = "Remove history"
		self.toolRead = "Mark all tweets as read"
		self.toolMode = "Messages"
		self.toolSettings = "Open preferences"
		self.toolAbout = "Some information about Atarashii"
		self.toolQuit = "Quit Atarashii"
		
		self.toolRefreshMessage = "Refresh message"
		self.toolHistoryMessage = "Remove history"
		self.toolReadMessage = "Mark all messages as read"
		
		# Menu
		self.menuUpdate = "Refresh"
		self.menuSettings = "Preferences"
		self.menuAbout = "About Atarashii"
		self.menuQuit = "Quit"
		
		# Tabs
		self.tabsTweets = "Tweets"
		self.tabsMessage = "Messages"
		self.tabsTweetsNew = "Tweets<b>(%d)</b>"
		self.tabsMessageNew = "Messages<b>(%d)</b>"
		self.tabsTweetsLoading = "Tweets..."
		self.tabsMessageLoading = "Messages..."
		
		
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

