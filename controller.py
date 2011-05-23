from shet.client import shet_action

class Controller(object):
	"""A lighting controller mix-in.
	
	A controller has two things:
	
	- An action, get_state, which returns the current state of the controller.
	- An event, state_change, which fires whenever the state changes, with the
		new state as it's only argument.
	
	The state is represented by True/true (on), None/null (don't care), and
	False/false (off).
	
	To set the state in python, call set_state -- this generally shouldn't be
	exposed to shet.
	
	This class should probably be mixed-in with ShetClient or a sub-class
	thereof.
	"""
	
	def __init__(self, default_state=None):
		# Default to 'don't care'.
		self._state = default_state
		self.state_change = self.add_event("state_change")
		
		# Helps restarting work properly.
		self.state_change(self._state)
	
	
	@shet_action
	def get_state(self):
		return self._state
	
	
	def set_state(self, state):
		"""Set the state of this controller."""
		if state not in [True, None, False]:
			raise Exception("State must be true, null, or false.")
		
		old_state, self._state = self._state, state
		
		if self._state != old_state:
			self.state_change(self._state)
	
