import datetime
from enum import Enum
import time
import pytz

SUBJECT = [
	"dedup",
	"vips",
	"blackscholes", 
	"canneal", 
	"radix",
	"freqmine",
	"ferret",  
	"scheduler", 
	"memcached"]

THREADS = "2"


class Event(Enum):
	START = "start"
	END = "end"
	UPDATE = "update_cores"
	PAUSE = "pause"
	UNPAUSE = "unpause"
	CUSTOME = "custom"

zurich_tz = pytz.timezone('Europe/Zurich')
# timezone_diff = datetime.timedelta(hours=2)

# RULES: 
# - each jobs should start and end, except for memcached who should only start
# - additional cpu usage (a list of CPU cores) should be logged for START and UPDATE events except for scheduler

class Logger:
	def __init__(self, opath):
		self.file = open(opath, 'w', buffering=1)

	def __log(self, event, subject, info = ""):
		cur_time = datetime.datetime.now().astimezone(zurich_tz).isoformat(timespec='microseconds')[:-6]
		# cur_time = (datetime.datetime.now() + timezone_diff).isoformat(timespec='microseconds')
		self.file.write(f'{cur_time} {event.value} {subject} {info} \n')

	def log_start(self, active_cores):
		self.__log(Event.START, SUBJECT[-2])
		self.__log(Event.START , SUBJECT[-1], active_cores)

	def log_end(self):
		self.__log(Event.END, SUBJECT[-2])

	def log_jobs(self, subject, event, active_cores=""):
		if event == Event.START:
			self.__log(event, subject, active_cores)
		else:
			self.__log(event, subject, active_cores)

	def log_custom(self, data):
		self.__log(Event.CUSTOME, data)

	def close(self):
		self.file.close()

if __name__ == "__main__":
    logger = Logger("testlog.txt")
    logger.log_start("[0]")
    logger.log_jobs(SUBJECT[0], Event.START, "[0]")
    logger.log_jobs(SUBJECT[0], Event.UPDATE, "[0,1]")
    logger.log_end()
    logger.close()
