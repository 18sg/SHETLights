from shet.client import ShetClient, shet_action, shet_property
from twisted.internet import reactor
from controller import Controller
import sys

import time
import ephem


"""
A controller which is false (off) during daylight hours and null (on as needed)
during night-time hours.
"""


class DaylightController(ShetClient, Controller):
	
	# The type of transition that occurred
	RISES = 1
	SETS  = 2
	
	def __init__(self, root, lat, long, leeway = 30*60):
		self.root = root
		
		# Goodness knows why this library wants a string
		self.observer = ephem.Observer()
		self.observer.lat  = str(lat)
		self.observer.long = str(long)
		
		# This is the body we care about
		self.sun = ephem.Sun()
		
		# How long before sunset/after sunrise should the lights still turn on
		self.leeway = leeway
		
		ShetClient.__init__(self)
		Controller.__init__(self, None)
		
		# Allow overriding
		self.add_action("override_state", self.set_state)
		
		# Start the process
		self.update_state()
	
	
	def update_state(self):
		(transition, delay) = self.get_next_transition()
		
		print "update_state:", (transition, delay)
		
		# Set the state of the lights appropriately
		if transition == DaylightController.RISES:
			self.set_state(None)
		else:
			self.set_state(False)
		
		
		# Call after the specified delay. Add a second to ensure that we pass the
		# rise/set point each time. (Legit...)
		reactor.callLater(delay+1, self.update_state)
	
	
	def get_next_transition(self):
		"""
		Returns the next transition to occur (RISES or SETS) and the number of
		seconds until that time.
		"""
		
		def ephem_to_unix(t):
			return time.mktime(ephem.localtime(t).timetuple())
		
		self.sun.compute()
		rises = ephem_to_unix(self.observer.next_rising(self.sun)) + self.leeway
		sets  = ephem_to_unix(self.observer.next_setting(self.sun)) - self.leeway
		now   = ephem_to_unix(ephem.now())
		
		# If sunset (with leeway) has already happened (unbenonced to ephem) then it
		# is not the next transition so just push it past the rise time so that it
		# is picked
		if sets < now:
			sets = rises + 1
		
		return (DaylightController.RISES if rises < sets else
		        DaylightController.SETS,
		        min(rises, sets) - now)
	


if __name__ == "__main__":
	SettableController(sys.argv[1]).run()
	

