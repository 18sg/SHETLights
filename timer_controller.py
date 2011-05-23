from shet.client import ShetClient, shet_action, shet_property
from twisted.internet import reactor
import sys
from controller import Controller

class TimerController(ShetClient, Controller):
	
	def __init__(self, root, default_timeout=None, default_state=None):
		self.root = root
		self.default_timeout = default_timeout
		self.default_state = default_state
		self.timer = None
		
		ShetClient.__init__(self)
		
		Controller.__init__(self, default_state)
		
		self.on_timed_out = self.add_event("timed_out")
		
		self.on_start = self.add_event("on_start")
	
	
	# Get and set the default timeout.
	@shet_property("default_timeout")
	def default_timeout_prop(self):
		return self.default_timeout
	
	@default_timeout_prop.set
	def set_default_timeout(self, timeout):
		self.default_timeout = timeout
	
	
	# Get and set the default state.
	@shet_property("default_state")
	def default_state_prop(self):
		return self.default_state
	
	@default_state_prop.set
	def set_default_state(self, state):
		self.default_state = state
	
	
	# Get the timeout, either from an argument, or the default timeout.
	# Throws an exception if none is found.
	def get_timeout(self, timeout):
		if timeout is not None:
			return timeout
		elif self.default_timeout is not None:
			return self.default_timeout
		else:
			raise Exception("No timeout set or specified.")
	
	# Start or reset the timer.
	# If no timeout is specified, the default will be used.
	@shet_action
	def start(self, state, timeout=None):
		timeout = self.get_timeout(timeout)
		
		self.on_start(timeout)
		
		if self.timer is None or not self.timer.active():
			self.timer = reactor.callLater(timeout, self.timed_out)
		else:
			self.timer.reset(timeout)
		
		self.set_state(state)
	
	@shet_action
	def on(self, timeout=None):
		self.start(True, timeout)
	
	@shet_action
	def off(self, timeout=None):
		self.start(False, timeout)
	
	# Ran when the timer finishes.
	def timed_out(self):
		# Discard the timer, reset the state, and raise timed_out.
		self.timer = None
		self.set_state(self.default_state)
		self.on_timed_out()
	
	@shet_action
	def finish(self):
		# This is possibly a hack, I'm not sure...
		self.timed_out()
	
	# Is the timer running?
	@shet_action
	def running(self):
		return self.timer is not None and self.timer.active()
	
	# How long is left on the timer.
	# Returns none if it's not running.
	@shet_action
	def time_left(self):
		if self.timer is None or not self.timer.active():
			return None
		else:
			return self.timer.getTime() - reactor.seconds()


if __name__ == "__main__":
	TimerController(sys.argv[1], float(sys.argv[2]) if len(sys.argv) > 2 else None).run()
