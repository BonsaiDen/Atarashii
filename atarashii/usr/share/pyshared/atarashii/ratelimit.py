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


# Ratelimit Thread -------------------------------------------------------------
# ------------------------------------------------------------------------------
import threading
import time
import calendar
import gobject

class RateLimiter(threading.Thread):
	def __init__(self, updater):
		threading.Thread.__init__(self)
		self.updater = updater
		self.main = updater.main
	
	def run(self):
		# Catch Errors
		try:
			req = self.main.api.rate_limit_status()
		
		except Exception, error:
			gobject.idle_add(lambda: self.main.gui.showError(error))
			return
		
		minutes = (req['reset_time_in_seconds'] - calendar.timegm(time.gmtime())) / 60
		limit = req['remaining_hits']
		if limit > 0:
			limit = limit / (2.0 + (2.0 / 5))
			self.main.refreshTimeout = int(minutes / limit * 60 * 1.10)
			if self.main.refreshTimeout < 45:
				self.main.refreshTimeout = 45
		
		# Check for ratelimit
		count = req['hourly_limit']
		if count < 150:
			if not self.main.rateWarningShown:
				self.main.rateWarningShown= True
				gobject.idle_add(lambda: self.main.gui.showWarning(count))
		
		else:
			self.main.rateWarningShown = False

