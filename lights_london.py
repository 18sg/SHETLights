from bind import *
from twisted.internet import task
from settable_controller import SettableController
from daylight_controller import DaylightController
from timer_controller import TimerController
from aggregator import Aggregator
from shet.client import ShetClient, shet_action
from twisted.internet import reactor
import random
from undergroundStatus import status
from time import sleep, localtime

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
		self.displayingLines = False
		self.current_rand = (0,0,0)
		self.lineStatus = {'District': {'status':'GS', 'color': (0,40,0)}, 'Hammersmith and City': {'status':'GS','color':(205,10,11)}, 'Circle': {'status':'GS','color':(140,80,0)}}
		self.statuses = {'MD':(255,25,0), 'SD':(255,0,0), 'CS':(255,0,0)}
		self.watch_event("backend/state_change", self.on_state_change)
		self.watch_event("/stairs/pir_top", self.display_lines)
		self.watch_event("/stairs/pir_bottom", self.display_lines)
		task.LoopingCall(self.random_step).start(5.0)
		#self.update_thread()
	
	def on_state_change(self, state):
		self.bright = state
		self.update_lights()
	
	def update_lights(self):
		self.set([y for x,y in zip(self.current_rand, (128,0,0))] if self.bright else
				self.current_rand)
	
	def set(self, new):
		for color in range(3):
			if new[color] != self.rgb[color]:
				self.call("/stairs/set_rgb_" + colors[color], new[color])
		self.rgb = new
	
	def random_step(self):
		if not self.displayingLines:
			def clamp(value):
				return max(0, min(value, 10))

			def updateR(self):
				self.r = clamp(self.r + random.randint(-1,1))

			def updateG(self):
				self.g = clamp(self.g + random.randint(-1,1))

			def updateB(self):
				self.b = clamp(self.b + random.randint(-1,1))
		
			self.r,self.g,self.b = self.current_rand

			updateFuncs = [updateR, updateG, updateB]
			random.choice(updateFuncs)(self)

			self.current_rand = self.r,self.g,self.b
			self.update_lights()

	def done_lines(self):
		self.displayingLines = False;

	def display_line(self, line):
		self.set((0,0,0))
		reactor.callLater(0.5, self.set, line['color'])
		reactor.callLater(2.5, self.set, self.statuses[line['status']])

	def display_lines(self):
		if (localtime().tm_hour in [7,8,9]) and (not self.displayingLines):
			for line in self.lineStatus:
				self.lineStatus[line]['status'] = status.getStatus(line)

			linesToShow = [lineInfo for lineName,lineInfo in self.lineStatus.iteritems() if lineInfo['status'] in self.statuses]

			if linesToShow:
				self.displayingLines = True;
				for index, line in enumerate(linesToShow):
					reactor.callLater(3.5*index, self.display_line, line)
				
				reactor.callLater(3.5*len(linesToShow), self.done_lines)

	def update_thread(self):
		for line in self.lineStatus:
			self.lineStatus[line]['status'] = status.getStatus(line)

		linesToShow = [lineInfo for lineName,lineInfo in self.lineStatus.iteritems() if lineInfo['status'] in self.statuses]

		if linesToShow:
			for index, line in enumerate(linesToShow):
				reactor.callLater(3.5*index, self.display_status, line)
				
			reactor.callLater(3.5*len(linesToShow), self.update_thread)
		else:
			self.random_step()
			reactor.callLater(5, self.update_thread)


Frontend().install()
reactor.run()
