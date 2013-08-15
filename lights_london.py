from bind import *
from daylight_controller import DaylightController
from shet.client import ShetClient, shet_action
from controller import Controller
from aggregator import Aggregator
from twisted.internet import reactor, defer
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
		LightRoutine.__init__(self, "random")

	def clamp(self, value):
		return max(0, min(value, 10))

	def updateR(self):
		self.r = self.clamp(self.r + random.randint(-1,1))

	def updateG(self):
		self.g = self.clamp(self.g + random.randint(-1,1))

	def updateB(self):
		self.b = self.clamp(self.b + random.randint(-1,1))	

	def run(self):
		LightRoutine.run(self)
		self.r,self.g,self.b = self.current_rand

		updateFuncs = [self.updateR, self.updateG, self.updateB]
		random.choice(updateFuncs)()

		self.current_rand = self.r,self.g,self.b
		self.setLights(self.current_rand)
		sleep(5)
		self.finished()

class Lines(LightRoutine):
	def __init__(self):
		self.undergroundRoot = "/underground/"

		self.lineColour = {'District': (0,40,0), 
							'Hammersmith and City': (205,10,11), 
							'Circle': (140,80,0),
							}
		self.statuses = {'MD':(255,25,0), 
							'SD':(255,0,0), 
							'CS':(255,0,0),
							'GS':(0,80,0),
							}
		self.watchedLines = ['District', 
								'Hammersmith and City',
								'Circle',
								]
		self.watchedStatuses = ['MD',
								'SD',
								'CS',
								'GS',
								]
		LightRoutine.__init__(self, "lines")

	def display_line(self, line, status):
		self.setLights((0,0,0))
		sleep(0.5)
		self.setLights(self.lineColour[line])
		sleep(2.5)
		self.setLights(self.statuses[status])
		sleep(1)

	def run(self):
		LightRoutine.run(self)
		for line in watchedLines:
			status = (yield self.client.get(self.undergroundRoot + line + "/status_id"))
			if status in watchedStatuses:
				yield self.display_line(line, status)
				self.finished()
		
class Bright(LightRoutine):
	def __init__(self):
		self.time = localtime()
		LightRoutine.__init__(self, "bright")

	def standby(self):
		self.time = localtime()

	def run(self):
		LightRoutine.run(self)
		elapsed = mktime(localtime()) - mktime(self.time) 
		if elapsed < 8:
			self.setLights((128,0,0))
			sleep(10 - elapsed)
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

	def on_state_change(self, state):
		if not state:
			self.popRoutine()

	def pushRoutine(self, routine):
		yield self.call(routine+"/standby")

		if routine not in self.routineQueue:
			self.routineQueue.append(routine)

	def popRoutine(self):
		print("popping routine")
		if len(self.routineQueue) > 0:
			routine = self.routineQueue.pop(0)
			yield self.call(routine+"/run")
		else:
			yield self.call(root+"/random/run")

	def pirTrig(self):
		if (localtime().tm_hour in [7,8,9]):
			self.pushRoutine("lines")
		if (yield self.get("/lights/daylight/get_state")) != "null":
			self.pushRoutine("bright")

Random().install()
Lines().install()
Bright().install()
Aggregator(root, ["random", "lines", "bright"]).install()
Frontend().install()
reactor.run()
