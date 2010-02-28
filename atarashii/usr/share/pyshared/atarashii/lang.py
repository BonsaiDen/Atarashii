# -*- coding: UTF-8 -*-

#  This file is part of  Atarashii.
#
#   Atarashii is free software: you can redistribute it and/or 
#  modify it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#   Atarashii is distributed in the hope that it will be useful,
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
		self.htmlReply = "%s antworten"
		self.htmlRetweet = "%s retweeten"
		self.htmlTime = "Getwittert um %H:%M:%S Uhr"
		self.htmlTimeDay = "Getwittert am %d.%m um %H:%M:%S Uhr"
		self.htmlSearch = "Suche nach &quot;%s&quot;"
		self.htmlBy = " von %s"
		self.htmlInReply = "in Antwort auf %s"
		self.htmlLoadMore = "Ältere Tweets"
		self.htmlEmpty = "Keine Tweets."
		
		self.htmlAboutSecond = 'vor ungefähr einer Sekunde'
		self.htmlSecond = 'vor %d Sekunden'
		self.htmlAboutMinute = 'vor ungefähr einer Minute'
		self.htmlMinute = 'vor %d Minuten'
		self.htmlAboutHour = 'vor ungefähr einer Stunde'
		self.htmlHour = 'vor %d Stunden'
		self.htmlAboutDay = 'vor ungefähr einem Tag'
		self.htmlDay = 'vor %d Tagen'
		
		# Text
		self.textEntry = "Was passiert gerade?"
		
		# Status
		self.statusLogout = "Nicht verbunden."
		self.statusConnecting = "Verbinde als %s..."
		self.statusConnected = "Verbunden, aktualisiere Tweets..."
		self.statusError = "Verbindung fehlgeschlagen."
		self.statusSeconds = "Update in %s Sekunden."
		self.statusOneSecond = "Update in einer Sekunde."
		self.statusMinute = "Update in einer Minute."
		self.statusMinutes = "Update in %d Minuten."
		
		self.statusUpdate = "Updating..."
		self.statusReply = "Antworte %s..."
		self.statusRetweet = "Retweete %s..."
		self.statusSend = "Aktualisiere Status..."
		self.statusLeft = "Noch %d Zeichen."
		self.statusMore = "%d Zeichen zu viel."
		self.statusLoadHistory = "Lade Tweets..."
		
		self.statusReconnectSeconds = "Automatischer Reconnect in %d Sekunden."
		self.statusReconnectMinute = "Automatischer Reconnect in einer Minute."
		self.statusReconnectMinutes = "Automatischer Reconnect in %d Minuten."
		
		# Reply
		self.labelReply = "<b>Antwort an %s:</b>"
		self.labelReplyText = "<b>Antwort auf:</b> %s"
		self.labelRetweet = "<b>%s retweeten:</b>"
		
		# Settings
		self.settingsTitle = "Einstellungen"
		self.settingsUsername = "Benutzername:"
		self.settingsPassword = "Passwort:"
		self.settingsButton = "Speichern"
		self.settingsNotify = "Benachrichtigungen"
		self.settingsSound = "Sound abspielen"
		self.settingsFile = "Sounddatei"
		self.settingsFileFilter = "Soundateien"
		
		# About
		self.aboutTitle = "Über Atarashii"
		self.aboutLicenseButton = "Lizenz"
		self.aboutOKButton = "OK"
		
		# Error
		self.errorButton = "OK"
		self.errorTitle = "Fehler"
 		self.errorLogin = "Falscher Benutzername oder Passwort."
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
		self.menuUpdate = "Tweets updaten"
		self.menuSettings = "Einstellungen"
		self.menuAbout = "Über Atarashii"
		self.menuExit = "Beenden"
		
		# Toolbar
		self.toolRefresh = "Tweets aktualisieren"
		self.toolHistory = "Ältere Tweets leeren"
		self.toolRead = "Alle Tweets als gelesen makieren"
		self.toolSettings = "Einstellungen öffnen"
		self.toolAbout = "Atarashii Info einblenden"
		self.toolQuit = "Atarashii beenden"
		

class LangEN:
	def __init__(self):
		# HTML
		self.htmlWelcome = "Welcome to Atarashii!"
		self.htmlLoading = "Loading Tweets..."
		self.htmlInfo = "Name: %s\nFollower: %d\nFollowing: %d\nTweets: %d"
		self.htmlProfile = "%s profile"
		self.htmlReply = "Reply to %s"
		self.htmlRetweet = "Retweet %s"
		self.htmlTime = "Tweeted at %H:%M:%S"
		self.htmlTimeDay = "Tweeted on %d.%m at %H:%M:%S"
		self.htmlSearch = "Search for &quot;%s&quot;"
		self.htmlBy = " by %s"
		self.htmlInReply = "in reply to %s"
		self.htmlLoadMore = "More tweets"
		self.htmlEmpty = "No tweets."
		
		self.htmlAboutSecond = 'about one second ago'
		self.htmlSecond = '%d seconds ago'
		self.htmlAboutMinute = 'about a minute ago'
		self.htmlMinute = '%d minutes ago'
		self.htmlAboutHour = 'about an hour ago'
		self.htmlHour = '%d hours ago'
		self.htmlAboutDay = 'about a day ago'
		self.htmlDay = '%d days ago'
		
		# Text
		self.textEntry = "What's happening?"
		
		# Status
		self.statusLogout = "Not connected."
		self.statusConnecting = "Connecting as %s..."
		self.statusConnected = "Connected, loading tweets..."
		self.statusError = "Connection failed."
		self.statusSeconds = "Update in %s seconds."
		self.statusOneSecond = "Update in one second."
		self.statusMinute = "Update in one minute."
		self.statusMinutes = "Update in %d minutes."
		
		self.statusUpdate = "Updating..."
		self.statusReply = "Replying to %s..."
		self.statusRetweet = "Retweeting %s..."
		self.statusSend = "Sending status..."
		self.statusLeft = "%d chars left."
		self.statusMore = "%d chars too much."
		self.statusLoadHistory = "Loading tweets..."
		
		self.statusReconnectSeconds = "Automatic reconnect in %d seconds."
		self.statusReconnectMinute = "Automatic reconnect in one minute."
		self.statusReconnectMinutes = "Automatic reconnect in %d minutes."
			
		
		# Reply
		self.labelReply = "<b>Reply to %s:</b>"
		self.labelReplyText = "<b>Reply on:</b> %s"
		self.labelRetweet = "<b>Rewteet %s:</b>"
		
		# Settings
		self.settingsTitle = "Settings"
		self.settingsUsername = "Username:"
		self.settingsPassword = "Password:"
		self.settingsButton = "Save"
		self.settingsNotify = "Notifications"
		self.settingsSound = "Play sound"
		self.settingsFile = "Soundfile"
		self.settingsFileFilter = "Soundfiles"
		
		# About
		self.aboutTitle = "About Atarashii"
		self.aboutLicenseButton = "License"
		self.aboutOKButton = "OK"
		
		# Error
		self.errorButton = "OK"
		self.errorTitle = "Error"
 		self.errorLogin = "Wrong Username oder Password."
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
		self.toolRefresh = "Update tweets"
		self.toolHistory = "Remove history"
		self.toolRead = "Mark all tweets as read"
		self.toolSettings = "Open settings"
		self.toolAbout = "Information about Atarashii"
		self.toolExit = "Exit Atarashii"
		
		# Menu
		self.menuUpdate = "Update tweets"
		self.menuSettings = "Settings"
		self.menuAbout = "About Atarashii"
		self.menuQuit = "Quit"
		
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

