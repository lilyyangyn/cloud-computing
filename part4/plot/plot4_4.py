import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter
import numpy as np
import argparse
from enum import Enum
from datetime import datetime
import datetime as dt

RUNS = 3

PART = "4_3"

LABELS = ["blackscholes", 
			"canneal", 
			"dedup", 
			"ferret", 
			"freqmine", 
			"radix", 
			"vips"]

class Event(Enum):
	START = "start"
	END = "end"
	UPDATE = "update_cores"
	PAUSE = "pause"
	UNPAUSE = "unpause"
	CUSTOME = "custom"

COLORS = ["#CCA000", "#CCCCAA", "#CCACCA", "#AACCCA", "#0CCA00", "#00CCA0", "#CC0A00"]


def read_file_logs(p, filename):
	logs = {}
	with open(p + "/" + filename, 'r') as f:
		for line in f:
			data = line.split()
			if len(data) < 3:
				continue

			subject = data[2]
			if subject not in logs:
				logs[data[2]] = []

			value = [datetime.strptime(data[0], '%Y-%m-%dT%H:%M:%S.%f').timestamp(), data[1]]
			if len(data) > 3:
				value.append(data[3])

			logs[data[2]].append(value)
	return logs

def read_file_latency(p, filename, start, end):
	raw_data = []
	real_qps = []
	start_times = []

	interval_num = 0 
	start_time = 0
	end_time = 0
	interval = 0
	header = True
	with open(p + "/" + filename, 'r') as f:
		for line in f:
			if "Total number of intervals" in line:
				interval_num = float(line.split()[5])
				continue
			if "Timestamp start" in line:
				start_time = float(line.split()[-1])/1000
				continue
			if "Timestamp end" in line:
				end_time = float(line.split()[-1])/1000
				interval = (end_time - start_time) / interval_num
				continue

			data = line.split()
			if len(data) != 18:
				continue

			if header:
				header = False
				continue

			if start_time > start:
				raw_data.append(float(data[12]))	# p95
				real_qps.append(float(data[16]))	# real qps
				start_times.append(start_time-start)	# start time
				if start_time > end:
					break
			start_time += interval

	return raw_data, real_qps, start_times

def plot(ipath, opath, run, save):
	run = run+1
	logs = read_file_logs(ipath, f'jobs_{run}.txt')

	startTime = logs["scheduler"][0][0]
	endTime = logs["scheduler"][1][0]

	job_segments = {}
	for label in LABELS:
		segs = []
		log = logs[label]
		for data in log:
			if data[1] == Event.START.value or data[1] == Event.UNPAUSE.value:
				segs.append([data[0] - startTime])
			elif data[1] == Event.PAUSE.value or data[1] == Event.END.value:
				segs[-1].append(data[0] - startTime)
		job_segments[label] = segs

	memcached_cpus = []
	memcached_timestamps = []
	log = logs["memcached"]
	for data in log:
		memcached_timestamps.append(data[0] - startTime)
		memcached_cpus.append(len(data[2].split(",")))

	qps_data = []
	latency_data = []
	raw_latency, raw_qps, start_times = read_file_latency(ipath, f'mcperf_{run}.txt', startTime, endTime)
	qps_data = np.array(raw_qps) / 1000
	latency_data = np.array(raw_latency) / 1000


	# ----------------------------------- Plotting -----------------------------------

	def plotA(ax):		
		ax.set_ylabel('95th Percentile Latency (ms)')
		ax.plot(start_times, latency_data, marker='o', markersize=2, linewidth=0.8)
		ax.tick_params(axis='y', labelcolor='tab:blue')
		ax.set_yticks(np.arange(0, 2.2, 0.2))
		ax.axhline(y=1, linestyle="dotted", color="black")

		ax1 = ax.twinx()
		ax1.set_ylabel('QPS')
		ax1.scatter(start_times, qps_data, c="tab:orange", s=5)
		ax1.tick_params(axis='y', labelcolor='tab:orange')
		ax1.set_yticks(np.arange(0, 110, 10))
		ax1.set_ylim([0, 100])
		ax1.yaxis.set_major_formatter(FormatStrFormatter('%dK'))

		ax.set_xticks(np.arange(0, start_times[-1], 50))
		ax.set_xlim([0, start_times[-1]])
		ax.set_xlabel('Time (ms)')
		ax.grid(linestyle= '--', axis='x')
		ax1.grid(linestyle= '--', axis='y')
		# ax.set_zorder(ax1.get_zorder() + 1)

		ax.set_title("Plot {}A".format(run))

	def plotB(ax):
		ax.set_ylabel('CPU core for Memcached')
		memcached_timestamps.append(endTime-startTime)
		memcached_cpus.append(memcached_cpus[-1])
		ax.plot(memcached_timestamps, memcached_cpus, markersize=2.5, linewidth=2)
		ax.tick_params(axis='y', labelcolor='tab:blue')
		ax.set_yticks(np.arange(0, 5, 1))
		ax.set_ylim([0, 5])

		ax1 = ax.twinx()
		ax1.set_ylabel('CPU')
		ax1.scatter(start_times, qps_data, c="tab:orange", s=5)
		ax1.tick_params(axis='y', labelcolor='tab:orange')
		ax1.set_yticks(np.arange(0, 110, 10))
		ax1.set_ylim([0, 100])
		ax1.yaxis.set_major_formatter(FormatStrFormatter('%dK'))

		ax.set_xticks(np.arange(0, start_times[-1], 50))
		ax.set_xlim([0, start_times[-1]])
		ax.set_xlabel('Time (ms)')
		ax.grid(linestyle= '--', axis='x')
		ax1.grid(linestyle= '--', axis='y')

		ax.set_title("Plot {}B".format(run))

	def plot_job_annotation(ax):
		for idx, label in enumerate(LABELS):
			for seg in job_segments[label]:
				ax.hlines(y=idx+1, xmin=seg[0], xmax=seg[1], color=COLORS[idx], lw=3.5)

		ax.set_yticks(range(len(LABELS)+2))
		ax.set_yticklabels([""] + LABELS + [""])
		# ax.tick_params(axis='y', labelsize=8)
		ax.grid(linestyle= '--')
		ax.set_xticks(np.arange(0, start_times[-1], 50))
		ax.set_xlim([0, start_times[-1]])

	fig, axes = plt.subplots(nrows=3, ncols=1, figsize=(14, 9), gridspec_kw={'height_ratios': [5, 5, 2]})
	plt.subplots_adjust(hspace=0.4)

	plotA(axes[0])
	plot_job_annotation(axes[2])
	plotB(axes[1])
	if not save:
		plt.show()
	else:
		plt.savefig("{}/benchmarkpart4_4_{}.pdf".format(opath, run), bbox_inches='tight')
		plt.clf()

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("-i", "--input", help="Input data path", default="../data/part4_4/1s")
	parser.add_argument("-s", "--save", help="Save plot", action="store_true")
	parser.add_argument("-o", "--output", help="Output data path", default="../data")
	args = parser.parse_args()

	for run in range(RUNS):
		plot(args.input, args.output, run, args.save)

