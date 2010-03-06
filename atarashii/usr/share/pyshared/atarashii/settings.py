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


# Settings ---------------------------------------------------------------------
# ------------------------------------------------------------------------------
import os
import urllib

class Settings:
	def __init__(self):
		self.dir = os.path.join(os.path.expanduser('~'), ".atarashii")
		if not os.path.exists(self.dir):
			os.mkdir(self.dir)

		self.values = {}
		self.load()
	
	# Load ---------------------------------------------------------------------
	def load(self):
		try:
			f = open(os.path.join(self.dir, 'atarashii.conf'), "r")
			lines = f.read().split('\n')
			for i in lines:
				name = i[:i.find(' ')]
				i = i[len(name)+1:]
				t = i[:i.find(' ')]
				value = i[len(t)+1:]
				try:
					if t == 'long':
						if value == "":
							value = long(-1)
						else:
							value = long(value)
					
					elif t == 'bool':
						value = True if value == "True" else False
					
					if name != "":
						self.values[urllib.unquote(name)] = value
				
				except Exception, detail:
					print detail
			
			f.close()
			
		except Exception, detail:
			self.values = {}
	
	# Save ---------------------------------------------------------------------
	def save(self):
		f = open(os.path.join(self.dir, 'atarashii.conf'), "w")
		keys = self.values.keys()
		keys.sort()
		for name in keys:
			value = self.values[name]
			c = type(value)
			if c == int or c == long:
				t = "long"
			
			elif c == bool:
				t = "bool"
			
			else:
				t = "str"
			
			f.write("%s %s %s\n" % (urllib.quote(name), t, value))
		
		f.close()
		
	# Get / Set ----------------------------------------------------------------
	def __getitem__(self, key):
		if self.values.has_key(key):
			return self.values[key]
		else:
			return None
	
	def __setitem__(self, key, value):
		self.values[key] = value
	
	def __delitem__(self, key):
		if self.values.has_key(key):
			del self.values[key]
	
	def isset(self, key):
		if self[key] != None:
			if type(self[key]) == long or type(self[key]) == int:
				return self[key] != -1
			else:
				return self[key].strip() != ""
	
	def isTrue(self, key, default = True):
		if self[key] == None:
			return default
			
		else:
			return self[key]
	
	def getAccounts(self):
		accounts = []
		for i in self.values.keys():
			if i.startswith("account_"):
				accounts.append(i[8:])
		
		accounts.sort()
		return accounts
				
