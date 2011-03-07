from shet.client import ShetClient, shet_action, shet_property
from twisted.internet import reactor
import exceptions
import sys


class Binding(ShetClient):
	
	def __init__(self, source, sink, *args):
		ShetClient.__init__(self)
		
		self.args = args
		self.init_source(source)
		self.init_sink(sink)
	
	def on_event(self, *args):
		self.raise_event(*args)


class BindingSource(object):
	
	def init_source(self, source):
		raise exceptions.NotImplementedError()


class BindingSink(object):
	
	def init_sink(self, source):
		raise exceptions.NotImplementedError()
	
	def raise_event(self, *args):
		raise exceptions.NotImplementedError()


class EventSource(BindingSource):
	
	def init_source(self, source):
		self.watch_event(source, self.on_event)


class ActionSource(BindingSource):
	
	def init_source(self, source):
		self.add_action(source, self.on_event)


class EventSink(BindingSink):
	
	def init_sink(self, sink):
		self.event = self.add_event(sink)
	
	def raise_event(self, *args):
		self.event(*(self.args if self.args else args))


class ActionSink(BindingSink):
	
	def init_sink(self, sink):
		self.sink = sink
	
	def raise_event(self, *args):
		self.call(self.sink, *(self.args if self.args else args))

class PropertySink(BindingSink):
	
	def init_sink(self, sink):
		self.sink = sink
	
	def raise_event(self, *args):
		self.set(self.sink, *(self.args if self.args else args))

class EventToEvent(Binding, EventSource, EventSink): pass
class EventToAction(Binding, EventSource, ActionSink): pass
class EventToProperty(Binding, EventSource, PropertySink): pass
class ActionToEvent(Binding, ActionSource, EventSink): pass
class ActionToProperty(Binding, ActionSource, PropertySink): pass

__all__ = ["EventToEvent", "EventToAction", "EventToProperty", "ActionToEvent", "ActionToProperty"]
