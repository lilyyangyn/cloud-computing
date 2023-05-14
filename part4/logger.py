import datetime
from enum import Enum

SUBJECT = ["blackscholes", 
			"canneal", 
			"dedup", 
			"ferret", 
			"freqmine", 
			"radix", 
			"vips", 
			"scheduler", 
			"memcached"]
    

class Event(Enum):
	START = "start"
	END = "end"
	UPDATE = "update_cores"
	PAUSE = "pause"
	UNPAUSE = "unpause"
	CUSTOME = "custom"

# RULES: 
# - each jobs should start and end, except for memcached who should only start
# - additional cpu usage (a list of CPU cores) should be logged for START and UPDATE events except for scheduler

class Logger:
	def __init__(self, opath):
		self.file = open(opath, 'w', buffering=1)

	def __log(self, event, subject, info=""):
		cur_time = datetime.datetime.now().isoformat(timespec='microseconds')
		if len(info) > 0:
			self.file.write(f'{cur_time} {event} {subject} {info}\n')
		else:
			self.file.write(f'{cur_time} {event} {subject}\n')

	def log_start(self, active_cores):
		self.__log(Event.START, SUBJECT[-2])
		self.__log(Event.START , SUBJECT[-1], active_cores)

	def log_end(self):
		self.__log(Event.END, SUBJECT[-2])

	def log_jobs(self, subject, event, active_cores=""):
		if active_cores == "":
			self.__log(event, subject)
		else:
			self.__log(event, subject, active_cores)

	def log_custom(self, data):
		self.__log(Event.CUSTOME, data)

	def close(self):
		self.file.close()

if __name__ == "__main__":
    logger = Logger("testlog.txt")
    logger.log_start("0")
    logger.log_jobs(SUBJECT[0], Event.UPDATE, "0,1")
    logger.log_end()
    logger.close()
