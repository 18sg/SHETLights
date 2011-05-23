from shet.client import ShetClient, shet_action, shet_property
from twisted.internet import reactor
from controller import Controller
import sys


class SettableController(ShetClient, Controller):
	
	def __init__(self, root, state=None):
		self.root = root
		
		ShetClient.__init__(self)
		Controller.__init__(self, state)
		
		self.add_action("set_state", self.set_state)


if __name__ == "__main__":
	SettableController(sys.argv[1]).run()
	
