from shet.client import ShetClient, shet_action, shet_property
from shet.path import join
from timer import Timer
from bind import *

class Light(ShetClient):
	
	def __init__(self, root, timeout, override_timeout=60):
		self.root = root
		
		ShetClient.__init__(self)
		
		self.on_change = self.add_event("on_change")
		
		self.timer_path = join(root, "timer")
		self.override_timer_path = join(root, "override")
		
		Timer(self.timer_path, timeout).install()
		Timer(self.override_timer_path, override_timeout).install()
		
		EventToAction(join(root, "timer", "timed_out"), join(root, "timer", "turn_off")).install()
		
		self.watch_event("override/timed_out", self.finish_override)
		self.override = False
		self.state = False
		self.saved_state = False
		self.timer_turn_on()
	
	@shet_action("timer/turn_off")
	def timer_turn_off(self):
		if not self.override:
			self._set_state(False)
		else:
			self.saved_state = False
	
	@shet_action("timer/turn_on")
	def timer_turn_on(self, *args):
		self.call("timer/start", *args)
		if not self.override:
			self._set_state(True)
		else:
			self.saved_state = True
	
	@shet_action("override/turn_off")
	def override_turn_off(self, *args):
		self.start_override(*args)
		self._set_state(False)
	
	@shet_action("override/turn_on")
	def override_turn_on(self, *args):
		self.start_override(*args)
		self._set_state(True)
	
	def finish_override(self):
		if self.override:
			self.restore_state()
			self.override = False
	
	def start_override(self, *args):
		self.call("override/start", *args)
		if not self.override:
			self.save_state()
			self.override = True
	
	def save_state(self):
		self.saved_state = self.state
	def restore_state(self):
		self._set_state(self.saved_state)
	
	
	@shet_property("state")
	def get_state(self):
		return self.state
	
	@get_state.set
	def set_state(self, state):
		self.start_override()
		self._set_state(bool(state))
	
	# Actually set the underlying switch state.
	def _set_state(self, state):
		if state != self.state:
			self.state = state
			self.on_change(1 if state else 0)
		
		
	@shet_property("override_on")
	def get_override_on(self):
		return self.override
		
	@get_override_on.set
	def set_override_on(self, mode):
		if mode:
			self.start_override()
		else:
			self.stop_override()
