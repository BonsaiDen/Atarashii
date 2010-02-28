#  This file is part of  Atarashii.
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
try:
	import gconf

except:
	from gnome import gconf

GCONF = gconf.client_get_default()

class Settings:
	def __init__(self):
		self.path = ("/" + "/".join(("apps", "atarashii"))) + "/SETTINGS"

	def __getitem__(self, key):
		value = GCONF.get("%s/%s" % (self.path, key))
		if value:
			return {
				"string": value.get_string,
				"int": value.get_int,
				"float": value.get_float,
				"bool": value.get_bool,
				"list": value.get_list}[value.type.value_nick]()

		else:
			return None

	def isset(self, key):
		return self[key] != None and self[key].strip() != ""


	def isTrue(self, key, default = True):
		if self[key] == None:
			return default
			
		else:
			return self[key]

	def __setitem__(self, key, value):
		if type(value).__name__ == "list":
			GCONF.set_list("%s/%s" % (self.path, key), gconf.VALUE_INT, value)

		else:
			{ "str": GCONF.set_string,
			"String": GCONF.set_string,
			"int": GCONF.set_int,
			"float": GCONF.set_float,
			"bool": GCONF.set_bool}[type(value).__name__](
			  "%s/%s" % (self.path, key), value)

		def bind(self, widget, key, **args):
			gwp.create_persistency_link(widget, "%s/%s" % (self.path, key), **args)
			return widget
		
		def notify(self, key, method):
			GCONF.notify_add("%s/%s" % (self.path, key), method)

