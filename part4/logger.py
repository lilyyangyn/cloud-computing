import time
from enum import Enum
START = "Start"
END = "End"

class Object(Enum):
    CONTROLLER = "Controller"
    MEMCACHED = "Memcached"
    BLACKSCHOLES = "Blackscholes"
    CANNEL = "Canneal"
    DEDUP = "Dedup"
    FERRET = "Ferret"
    FREQMINE = "Freqmine"
    RADIX = "Radix"
    VIPS = "Vips"



class Event(Enum):
	START = "Start"
	PAUSE = "Pause"
	UNPAUSE = "Unpause"
	END = "End"

class Logger:
	def __init__(self, opath):
		self.file = open(opath, 'w', buffering=1)

	def __log(self, object, info):
		self.file.write(f'{time.time()}, {object}, {info}\n')

	def log_start(self):
		self.__log(Object.CONTROLLER, Event.START)

	def log_end(self):
		self.__log(Object.CONTROLLER, Event.END)

	def log_container(self, container, event):
		self.__log(container, event)

	def log_memcached(self, ncpus):
		self.__log(Object.MEMCACHED, ncpus)
	
	def close(self):
		self.file.close()

