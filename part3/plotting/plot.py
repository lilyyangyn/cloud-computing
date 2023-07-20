from datetime import datetime
import json
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter
import numpy as np
import argparse

# LABELS = ["blackscholes", "canneal", "dedup", "ferret", "freqmine", "radix", "vips"]
# COLORS = ["#CCA000", "#CCCCAA", "#CCACCA", "#AACCCA", "#0CCA00", "#00CCA0", "#CC0A00"]
# NODES = ["node-a-2core", "node-b-4core", "node-c-8core"]
allocs = {"node-a-2core":["vips", "dedup"], "node-b-4core":["blackscholes", "canneal"], "node-c-8core":["freqmine", "radix", "ferret"]}
colors = {"blackscholes":"#CCA000", "canneal":"#CCCCAA", "dedup":"#CCACCA", "ferret":"#AACCCA", "freqmine":"#0CCA00", "radix":"#00CCA0", "vips":"#CC0A00"}

def read_mcperf_res(path, filename):
	p95 = []
	duration = []
	with open(path + "/" + filename, 'r') as f:
		for line in f:
			if "#type" in line:
				continue
			data = line.split()
			if len(data) < 18:
				continue
			p95.append(float(data[12]))
			duration.append(float(data[-1])-float(data[-2]))

	return p95, duration

def read_parsec_res(path, filename):
	time_format = '%Y-%m-%dT%H:%M:%SZ'
	file = open(path + "/" + filename, 'r')
	json_file = json.load(file)


	jobs = {}
	start_times = []
	completion_times = []
	for item in json_file['items']:
		name = str(item['status']['containerStatuses'][0]['name'])
		if "parsec-" in name:
			name = name[7:]
		if name != "memcached":
			start_time = datetime.strptime(
						item['status']['containerStatuses'][0]['state']['terminated']['startedAt'],
						time_format)
			completion_time = datetime.strptime(
					item['status']['containerStatuses'][0]['state']['terminated']['finishedAt'],
					time_format)
			start_times.append(start_time)
			completion_times.append(completion_time)
			jobs[name] = (start_time, completion_time, completion_time-start_time)
	file.close()
	for i in jobs.keys():
		jobs[i] = (int((jobs[i][0]-min(start_times)).total_seconds()), int((jobs[i][1]-min(start_times)).total_seconds()), int(jobs[i][2].total_seconds()))
	# print(jobs)
	return jobs


def plot(ipath, opath, save, file, parsec):
	raw_p95, raw_duration = read_mcperf_res(ipath, file)
	duration = [i/1000 for i in raw_duration]
	p95 = [i/1000 for i in raw_p95]

	jobs = read_parsec_res(ipath, parsec)


	# fig = plt.figure(0, figsize=(20, 8))
	# ax = fig.add_subplot(111)
	
	fig, axes = plt.subplots(nrows=2, ncols=1, figsize=(14, 9), gridspec_kw={'height_ratios': [5, 5]})
	plt.subplots_adjust(hspace=0.4)

	def plot_bar(ax):
		ax.bar([i * 10 + 5 for i in range(len(p95))], p95, width=[i/1.1 for i in duration])
		ax.set_xlim([0, 250])		
		ax.set_ylim([0, 1])		
		ax.set_xticks(np.arange(0, 250, 10))
		ax.set_yticks(np.arange(0, 1, 0.2))	
		ax.set_xlabel('Time (s)')
		ax.set_ylabel('95th Percentile Latency (ms)')
		ax.grid(linestyle= '--')
		ax.set_title("Run 3\n\nmemcached 95th Percentile Latency")
	
	def plot_timeline(ax):
		for idx, node in enumerate(list(allocs.keys())):
			jobs_on_node = allocs[node]
			for j in jobs_on_node:
				ax.hlines(y=idx+1, xmin=jobs[j][0], xmax=jobs[j][1], color=colors[j], lw=5, label=j)
		ax.set_xlim([0, 250])
		ax.set_xticks(np.arange(0, 250, 10))
		ax.set_yticks(range(len(allocs.keys())+2))
		ax.set_yticklabels([""] + list(allocs.keys()) + [""])
		ax.grid(linestyle= '--')
		ax.set_title("PARSEC Jobs")
		ax.legend(loc='lower right')
	
	plot_bar(axes[0])
	plot_timeline(axes[1])
	if not save:
		plt.show()
	else:
		plt.savefig(opath+'/benchmark_3.pdf', bbox_inches='tight')
		plt.clf()

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("-i", "--input", help="Input data path", default="/Users/kehongliu/Downloads/part_3_results_group_49")
	parser.add_argument("-m", "--memcached", help="memcached file name", default="mcperf_3.txt")
	parser.add_argument("-p", "--parsec", help="parsec file name", default="pods_3.json")
	parser.add_argument("-s", "--save", help="Save plot", action="store_true", default=True)
	parser.add_argument("-o", "--output", help="Output data path", default="/Users/kehongliu/Downloads")
	args = parser.parse_args()

	plot(args.input, args.output, args.save, args.memcached, args.parsec)

