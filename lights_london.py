from bind import *
from twisted.internet import task
from settable_controller import SettableController
from daylight_controller import DaylightController
from timer_controller import TimerController
from aggregator import Aggregator
from shet.client import ShetClient, shet_action
from twisted.internet import reactor
import random

DaylightController("/lights/daylight", 53.46171, -2.217164).install()

TimerController("/stairs/light/backend/timer", 10, False).install()
TimerController("/stairs/light/backend/override", 10, None).install()
Aggregator("/stairs/light/backend",
           ["override", "/lights/daylight", "timer"]).install()

EventToAction("/stairs/pir_top", "/stairs/light/backend/timer/on").install()
EventToAction("/stairs/pir_bottom", "/stairs/light/backend/timer/on").install()

colors = "red green blue".split()

class Frontend(ShetClient):
	root = "/stairs/light"
	
	def __init__(self):
		self.rgb = (0,0,0)
		ShetClient.__init__(self)
		self.bright = False
		self.watch_event("backend/state_change", self.on_state_change)
		self.current_rand = (0,0,0)
		task.LoopingCall(self.random_step).start(5.0)
	
	def on_state_change(self, state):
		self.bright = state
		self.update_lights()
	
	def update_lights(self):
		self.set([x+y for x,y in zip(self.current_rand, (128,0,0))] if self.bright else
				self.current_rand)
	
	def set(self, new):
		for color in range(3):
			if new[color] != self.rgb[color]:
				self.call("/stairs/set_rgb_" + colors[color], new[color])
		self.rgb = new
	
	def random_step(self):
		def clamp(value):
			return max(0, min(value, 20))
		
		r,g,b = self.current_rand
		r = clamp(r + random.randint(-1,1))
		g = clamp(g + random.randint(-1,1))
		b = clamp(b + random.randint(-1,1))
		self.current_rand = r,g,b
		self.update_lights()

Frontend().install()
reactor.run()
