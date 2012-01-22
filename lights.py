from bind import *

from settable_controller import SettableController
from aggregator import Aggregator
from timer_controller import TimerController
from shet.path import join

from twisted.internet import reactor

TimerController("/lights/override", 10*60, None).install()
SettableController("/lights/daylight", None).install()


def setup_light(name, time):
	Aggregator(name, ["/lights/override", "override", "/lights/daylight", "timer"]).install()
	TimerController(join(name, "timer"), time, False).install()
	TimerController(join(name, "override"), 10*60, None).install()


setup_light("/hall/lights", 120)
setup_light("/landing/lights", 120)
setup_light("/attic/lights", 120)
setup_light("/bog/lights", 120)
setup_light("/lounge/lights_new/lounge", 600)
setup_light("/lounge/lights_new/kitchen", 600)

EventToProperty("/hall/lights/state_change", "/karl/arduino/light_hall").install()
EventToProperty("/landing/lights/state_change", "/karl/arduino/light_landing").install()
EventToProperty("/bog/lights/state_change", "/jonathan/arduino/bogvo").install()
EventToProperty("/landing/lights/state_change", "/tom/servo").install()
EventToProperty("/lounge/lights_new/lounge/state_change", "/lounge/lights/lounge").install()
EventToProperty("/lounge/lights_new/kitchen/state_change", "/lounge/lights/kitchen").install()

EventToAction("/tom/pir_landing", "/attic/lights/timer/on").install()
EventToAction("/jonathan/arduino/bogir", "/bog/lights/timer/on").install()
EventToAction("/karl/arduino/pir_hall", "/hall/lights/timer/on").install()
EventToAction("/jonathan/arduino/stairir", "/landing/lights/timer/on").install()

EventToAction("/tom/pir_middle", "/landing/lights/timer/on").install()

EventToAction("/lounge/arduino/pir", "/lounge/lights_new/lounge/timer/on").install()
EventToAction("/lounge/arduino/pir", "/lounge/lights_new/kitchen/timer/on").install()




# pir_events = dict(hall="/karl/arduino/pir_hall",
#                   middle="/tom/pir_middle",
#                   landing="/tom/pir_landing",
#                   lounge="/lounge/arduino/pir")
# light_props = dict(hall="/karl/arduino/light_hall",
#                    middle="/karl/arduino/light_landing",
#                    landing="/tom/servo",
#                    lounge="/lounge/lights/lounge",
#                    kitchen="/lounge/lights/kitchen")
# pir_activates = dict(
# 	hall="hall".split(),
# 	middle="middle landing".split(),
# 	landing="landing".split(),
# 	lounge="lounge kitchen".split()
# )
# 
# shet /attic/lights/timer/on
# shet /bog/lights/timer/on
# shet /hall/lights/timer/on
# 
# shet /landing/lights/timer/on
# shet /attic/lights/timer/on
# 
# shet /lounge/lights_new/lounge/timer/on
# shet /lounge/lights_new/kitchen/timer/on

reactor.run()
