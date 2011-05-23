from timer import Timer
from bind import *
from light import Light
from twisted.internet import reactor


Light("/hall/lights", 120).install()
Light("/landing/lights", 120).install()
Light("/attic/lights", 120).install()
Light("/bog/lights", 120).install()
Light("/lounge/lights_new/lounge", 600).install()
Light("/lounge/lights_new/kitchen", 600).install()

EventToProperty("/hall/lights/on_change", "/karl/arduino/light_hall").install()
EventToProperty("/landing/lights/on_change", "/karl/arduino/light_landing").install()
EventToProperty("/bog/lights/on_change", "/jonathan/arduino/bogvo").install()
EventToProperty("/attic/lights/on_change", "/tom/servo").install()
EventToProperty("/lounge/lights_new/lounge/on_change", "/lounge/lights/lounge").install()
EventToProperty("/lounge/lights_new/kitchen/on_change", "/lounge/lights/kitchen").install()

EventToAction("/tom/pir_landing", "/attic/lights/timer/turn_on").install()
EventToAction("/jonathan/arduino/pir", "/bog/lights/timer/turn_on").install()
EventToAction("/karl/arduino/pir_hall", "/hall/lights/timer/turn_on").install()

#Temporary while the bulb is blown.
# EventToAction("/karl/arduino/pir_hall", "/landing/lights/timer/turn_on").install()
# Not temporary while trollin'.
EventToAction("/hall/lights/on_change", "/tom/reading").install()

EventToAction("/tom/pir_middle", "/landing/lights/timer/turn_on").install()
EventToAction("/tom/pir_middle", "/attic/lights/timer/turn_on").install()

EventToAction("/lounge/arduino/pir", "/lounge/lights_new/lounge/timer/turn_on").install()
EventToAction("/lounge/arduino/pir", "/lounge/lights_new/kitchen/timer/turn_on").install()




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
# shet /attic/lights/timer/turn_on
# shet /bog/lights/timer/turn_on
# shet /hall/lights/timer/turn_on
# 
# shet /landing/lights/timer/turn_on
# shet /attic/lights/timer/turn_on
# 
# shet /lounge/lights_new/lounge/timer/turn_on
# shet /lounge/lights_new/kitchen/timer/turn_on

reactor.run()
