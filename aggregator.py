from shet.client import ShetClient, shet_action, shet_property
from twisted.internet.defer import gatherResults
from controller import Controller
from shet.path import join
from functools import partial
import sys

class Aggregator(ShetClient, Controller):
	
	def __init__(self, root, controllers, default_state=False):
		self.root = root
		self.controllers = []
		self.default_state = default_state
		self.controller_states = {}
		self.watches = []
		
		ShetClient.__init__(self)
		# Default to off.
		Controller.__init__(self, False)
		
		# Do all the normal stuff when changing the controllers.
		self.set_controllers(controllers)
	
	# Update the state of an individual controller by calling it's get_state.
	# This is used for initialisation only.
	def update_state(self, controller):
		d = self.call(join(controller, "get_state"))
		def callback(state):
			self.controller_states[controller] = state
		d.addCallback(callback)
		return d
	
	# Update all the states of the controllers, and the output state.
	def update_states(self):
		# Perform the updates, *then* set the output state...
		d = gatherResults([self.update_state(controller)
		                  for controller in self.controllers])
		def callback(arg):
			self.set_state(self.get_out_state())
		d.addCallback(callback)
	
	# Get the output state, assuming the states of the controllers are set right.
	def get_out_state(self):
		# Because i don't want to delete it...
		# return ([self.controller_states[c]
		#          for c in self.controllers
		#          if self.controller_states[c] != None]
		#         or [self.default_state])[0]
		
		# Find the first controller with a not-none state.
		for controller in self.controllers:
			if self.controller_states[controller] is not None:
				return self.controller_states[controller]
		return self.default_state
	
	# Make sure the shet watches are consistent with the controllers.
	def update_watches(self):
		# Remove all watches
		for watch in self.watches:
			self.unwatch_event(watch)
		self.watches = []
		
		# Add watches for each controller.
		for controller in self.controllers:
			self.watch_event(join(controller, "state_change"),
			                 partial(self.on_change, controller))
	
	# Called when a controller changes state.
	def on_change(self, controller, value):
		self.controller_states[controller] = value
		self.set_state(self.get_out_state())
	
	# Get and set the list of controllers.
	@shet_property("controllers")
	def controllers_prop(self):
		return self.controllers
	
	@controllers_prop.set
	def set_controllers(self, controllers):
		self.controllers = controllers
		self.update_states()
		self.update_watches()


if __name__ == "__main__":
	Aggregator(sys.argv[1], []).run()
