from bind import *
from daylight_controller import DaylightController
from shet.client import ShetClient, shet_action
from controller import Controller
from aggregator import Aggregator
from shet.sync   import make_sync
from twisted.internet import reactor, defer
from functools import partial
import random
from time import localtime, mktime

DaylightController("/lights/daylight", 53.46171, -2.217164).install()

colors = ["red", "green", "blue",]

root = "/stairs/routines"


def sleep(secs):
	d = defer.Deferred()
	reactor.callLater(secs, d.callback, None)
	return d

class LightRoutine(ShetClient, Controller):
	def __init__(self, name):
		self.root = root+"/"+name
		ShetClient.__init__(self)
		Controller.__init__(self, None)
		self.add_action("standby", self.standby)
		self.add_action("run", self.run)

	def setLights(self, new):
		for color in range(3):
			self.call("/stairs/set_rgb_" + colors[color], new[color])

	def standby(self):
		pass

	def run(self):
		self.set_state(True)

	def finished(self):
		self.set_state(None)

class Random(LightRoutine):
	def __init__(self):
		self.current_rand = (0,0,0)
		self.delay = 5
		LightRoutine.__init__(self, "random")
		self.add_property("delay", self.get_delay, self.set_delay)

	def get_delay(self):
		return self.delay

	def set_delay(self, delay):
		self.delay = delay

	def clamp(self, value):
		return max(0, min(value, 10))

	def updateR(self):
		self.r = self.clamp(self.r + random.randint(-1,1))

	def updateG(self):
		self.g = self.clamp(self.g + random.randint(-1,1))

	def updateB(self):
		self.b = self.clamp(self.b + random.randint(-1,1))	

	@make_sync
	def run(self):
		LightRoutine.run(self)
		self.r,self.g,self.b = self.current_rand

		updateFuncs = [self.updateR, self.updateG, self.updateB]
		random.choice(updateFuncs)()

		self.current_rand = self.r,self.g,self.b
		self.setLights(self.current_rand)
		yield sleep(self.delay)
		self.finished()

class Lines(LightRoutine):
	def __init__(self):
		self.undergroundRoot = "/underground/"

		self.lines = {'District': (0,40,0), 
							'Hammersmith and City': (205,10,11), 
							'Northern': (0,0,0),
							'Overground': (170,14,0),
							'Bakerloo': (37,9,1),
							'Central': (100,0,0),
							'Circle': (140,80,0),
							'DLR': (0,50,18),
							'Jubilee': (2,2,2),
							'Metropolitan': (10,0,5),
							'Piccadilly': (0,0,20),
							'Victoria': (10,13,100),
							'Waterloo and City': (0,70,38),
							}
		self.statuses = {'Good Service':(0,80,0),
							'Minor Delays':(255,25,0), 
							'Bus Service':(255,0,0),
							'Reduced Service':(255,0,0),
							'Severe Delays':(255,0,0), 
							'Part Closure':(255,25,0),
							'Planned Closure':(255,25,0),
							'Part Suspended':(255,0,0),
							'Suspended':(255,0,0),
							}
		self.watchedLines = ['District', 
								'Hammersmith and City',
								'Circle',
								'Piccadilly',
								]
		self.delayStatuses = ['Minor Delays',
								'Bus Service',
								'Reduced Service',
								'Severe Delays',
								'Part Closure',
								'Planned Closure',
								'Part Suspended',
								'Suspended',
								]

		LightRoutine.__init__(self, "lines")

		self.add_action("all_lines", self.display_all_lines)
		self.add_action("all_delays", self.display_all_delays)
		for line in self.lines.keys():
			self.add_action(line, partial(self.display_line, line))

	@make_sync
	def display_line_status(self, line, status):
		self.setLights((0,0,0))
		yield sleep(0.5)
		self.setLights(self.lines[line])
		yield sleep(2.5)
		self.setLights(self.statuses[status])
		yield sleep(1)

	@make_sync
	def display_line(self, line):
		LightRoutine.run(self)
		status = (yield self.get(self.undergroundRoot + line + "/status_des"))
		self.setLights((0,0,0))
		yield sleep(0.5)
		self.setLights(self.lines[line])
		yield sleep(2.5)
		if status in self.statuses.keys():
			self.setLights(self.statuses[status])
			yield sleep(1)	
		self.finished()

	@make_sync
	def display_all_lines(self):
		LightRoutine.run(self)
		for line in self.lines.keys():
			status = (yield self.get(self.undergroundRoot + line + "/status_des"))
			if status in self.statuses.keys():
				yield self.display_line_status(line, status)
		self.finished()

	@make_sync
	def display_all_delays(self):
		LightRoutine.run(self)
		for line in self.lines.keys():
			status = (yield self.get(self.undergroundRoot + line + "/status_des"))
			if status in self.delayStatuses:
				yield self.display_line_status(line, status)
		self.finished()

	@make_sync
	def run(self):
		LightRoutine.run(self)
		for line in self.watchedLines:
			status = (yield self.get(self.undergroundRoot + line + "/status_des"))
			if status in self.delayStatuses:
				yield self.display_line_status(line, status)
		self.finished()
		
class Bright(LightRoutine):
	def __init__(self):
		self.time = localtime()
		LightRoutine.__init__(self, "bright")

	def standby(self):
		self.time = localtime()

	@make_sync
	def run(self):
		LightRoutine.run(self)
		elapsed = mktime(localtime()) - mktime(self.time) 
		if elapsed < 8:
			self.setLights((128,0,0))
			yield sleep(10 - elapsed)
		self.finished()

class Frontend(ShetClient):
	def __init__(self):
		self.root = root
		self.rgb = (0,0,0)	
		ShetClient.__init__(self)

		self.watch_event("state_change", self.on_state_change)
		self.watch_event("/stairs/pir_top", self.pirTrig)
		self.watch_event("/stairs/pir_bottom", self.pirTrig)

		self.routineQueue = []

		reactor.callWhenRunning(self.popRoutine)

	def on_state_change(self, state):
		if not state:
			self.popRoutine()

	@make_sync
	def pushRoutine(self, routine):
		if (yield self.call(routine + "/get_state")) == None:
			self.call(routine+"/standby")
			if routine not in self.routineQueue:
				self.routineQueue.append(routine)

	def popRoutine(self):
		if len(self.routineQueue) > 0:
			routine = self.routineQueue.pop(0)
			self.call(routine+"/run")
		else:
			self.call(root+"/random/run")

	@make_sync
	def pirTrig(self):
		noneQueued = (len(self.routineQueue) == 0)
		if (localtime().tm_hour in [7,8,9]):
			yield self.pushRoutine("lines")
		if ((yield self.call("/lights/daylight/get_state")) == None):
			yield self.pushRoutine("bright")
		if noneQueued and (len(self.routineQueue) > 0):
			self.popRoutine()

Random().install()
Lines().install()
Bright().install()
Aggregator(root, ["random", "lines", "bright"]).install()
Frontend().install()
reactor.run()
