from bind import *

from settable_controller import SettableController
# from daylight_controller import DaylightController
from aggregator import Aggregator
from timer_controller import TimerController
from shet.path import join
from shet.client import ShetClient, shet_action

from twisted.internet import reactor

TimerController("/lights/override", 10*60, None).install()
# DaylightController("/lights/daylight", 53.46171, -2.217164).install()

Aggregator("/tom/light/backend", ["alarm", "override", "/lights/daylight", "timer"]).install()
SettableController("/tom/light/backend/override").install()
TimerController("/tom/light/backend/timer", 300, False).install()
TimerController("/tom/light/backend/alarm", 60 * 30, None).install()
EventToAction("/tom/arduino/pir", "/tom/light/backend/timer/on").install()


class Frontend(ShetClient):
	root = "/tom/light"
	
	def __init__(self):
		ShetClient.__init__(self)
		self.watch_event("backend/state_change", self.on_state_change)
		self.set("/tom/arduino/light/fade_speed", 10)
	
	def on_state_change(self, state):
		self.call("/tom/arduino/light/fade", {False: 0, True: 255, None: 0}[state])
	
	@shet_action
	def on(self):
		return self.call("backend/override/set_state", True)
	
	@shet_action
	def off(self):
		return self.call("backend/override/set_state", False)
	
	@shet_action
	def auto(self):
		return self.call("backend/override/set_state", None)
	
	@shet_action
	def leave(self):
		self.call("backend/alarm/finish")
		self.call("backend/override/set_state", None)
		self.call("backend/timer/finish")
	
	@shet_action
	def wake_up(self):
		return self.call("backend/alarm/on")
	
	@shet_action
	def end_alarm(self):
		return self.call("backend/alarm/finish")

Frontend().install()

reactor.run()
