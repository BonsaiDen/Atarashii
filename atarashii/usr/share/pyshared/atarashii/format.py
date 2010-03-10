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


# Tweet Formatter --------------------------------------------------------------
# ------------------------------------------------------------------------------
import re, urllib
#urlRegex = re.compile("((mailto\:|(news|(ht|f)tp(s?))\://){1}[^\s\)\]]+)")
#atRegex = re.compile("\B@([a-zA-Z0-9_]{1,15})")
#tagRegex = re.compile('''\B#([^\-\+\)\(\[\]\?\=\*\}\{\:\.\;\,\"\'\!\<\>\|\s\~\&\§\$\%\/\\\\µ#]{1,})''')

# Some of this code has been translated from the twitter-text-java library:
# <http://github.com/mzsanford/twitter-text-java>
urlRegex = re.compile("((mailto\:|(news|(ht|f)tp(s?))\://){1}[^\s\)\]]+)")
atRegex = re.compile(ur"\B[@\uFF20]([a-z0-9_]{1,20})", re.UNICODE | re.IGNORECASE)
tagRegex = re.compile(ur"(^|[^0-9A-Z&/]+)(#|\uff03)([0-9A-Z_]*[A-Z_]+[\u00c0-\u00d6\u00d8-\u00f6\\u00f8-\u00ff]*)", re.UNICODE | re.IGNORECASE)

preChars = "(?:[^/\"':!=]|^|\\:)"
domainChars = "(?:[\\.-]|[^\\s])+\\.[a-z]{2,}(?::[0-9]+)?"
pathChars = "(?:[\\.,]?[a-z0-9!\\*'\\(\\);:=\\+\\$/%#\\[\\]\\-_,~@])"
  # Valid end-of-path chracters (so /foo. does not gobble the period).
  # 1. Allow ) for Wikipedia URLs.
  # 2. Allow =&# for empty URL parameters and other URL-join artifacts
  
pathEndingChars = "[a-z0-9\\)=#/]"
queryChars = "[a-z0-9!\\*'\\(\\);:&=\\+\\$/%#\\[\\]\\-_\\.,~]"
queryEndingChars = "[a-z0-9_&=#]"

urlRegex = re.compile("((" + preChars + ")((https?://|www\\.)(" + domainChars +\
					 ")(/" + pathChars + "*" + pathEndingChars + "?)?(\\?" + \
					 queryChars + "*" + queryEndingChars + ")?))",
					 re.UNICODE | re.IGNORECASE)

from lang import lang

class Formatter:
	def parse(self, text):
		self.urls = []
		self.users = []
		self.tags = []
		urlRegex.sub(self.url, text)
		
		
		# Filter URLS
		self.textParts = []
		last = 0
		for i in self.urls:
			self.textParts.append((0, text[last:i.start()]))
			self.textParts.append((1, text[i.start():i.end()]))
			last = i.end()
			
		self.textParts.append((0, text[last:]))

		# Filter @
		self.filterBy(atRegex, 2)
		

		# Filter Hashtags	
		self.filterBy(tagRegex, 3)
		
		# Replace all the stuff
		result = []
		for i in self.textParts:
			t, c = i
			if t == 0:
				result.append(c)
			
			# URL
			elif t == 1:
				if len(c) > 30:
					text = c[0:27] + "..."
				else:
					text = c
	
				result.append(
					'<a href="%s" title="%s">%s</a>' % 
					(self.escape(c), self.escape(c), text))
			
			# @
			elif t == 2:
				at = c[1:]
				self.users.append(at)
				result.append(
					('<a href="http://twitter.com/%s" title="' + lang.htmlAt +\
					'">@%s</a>') % (at, at, at))
			
			# tag
			elif t == 3:
				search = c[c.find('#')+1:]
				self.tags.append(search)
				result.append(
					('<a href="http://search.twitter.com/search?%s" title="' +\
					lang.htmlSearch + '">%s</a>') % 
					(urllib.urlencode({'q': '#' + search}), search, c))
		
		return "".join(result)

	# Crazy filtering and splitting :O
	def filterBy(self, regex, o):
		e = 0
		while e < len(self.textParts):
			t, c = self.textParts[e]
			if t == 0:
				m = regex.search(c)
				if m != None:
					self.textParts.pop(e)
					self.textParts.insert(e, (0, c[:m.start()]))
					self.textParts.insert(e + 1, (o, c[m.start():m.end()]))
					self.textParts.insert(e + 2, (0, c[m.end():]))
					e += 1
			
			e += 1
	
	def url(self, match):
		self.urls.append(match)
		
	# Regex stuff
	def escape(self, text):
		ent = {
			"&": "&amp;", 
			'"': "&quot;", 
			"'": "&apos;", 
			">": "&gt;", 
			"<": "&lt;"
		}
		return "".join(ent.get(c,c) for c in text)
		
