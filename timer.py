from shet.client import ShetClient, shet_action, shet_property
from twisted.internet import reactor
import sys

class Timer(ShetClient):
	
	def __init__(self, root, default_timeout=None):
		self.root = root
		self.default_timeout = default_timeout
		self.timer = None
		
		ShetClient.__init__(self)
		
		self.timed_out = self.add_event("timed_out")
		
		self.on_start = self.add_event("on_start")
	
	
	# The current default timeout.
	@shet_property("default_timeout")
	def default_timeout_prop(self):
		return self.default_timeout
	
	@default_timeout_prop.set
	def set_default_timeout(self, timeout):
		self.default_timeout = timeout
	
	
	# Get the timeout, either from an argument, or the dafault timeout.
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
	def start(self, timeout=None):
		timeout = self.get_timeout(timeout)
		
		self.on_start(timeout)
		
		if self.timer is None or not self.timer.active():
			self.timer = reactor.callLater(timeout, self.timed_out)
		else:
			self.timer.reset(timeout)
	
	@shet_action
	def finish(self):
		self.start(0)
	
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
	Timer(sys.argv[1], float(sys.argv[2]) if len(sys.argv) > 2 else None).run()
