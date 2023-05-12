import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter
import numpy as np
import argparse

LABELS = ["blackscholes", "canneal", "dedup", "ferret", "freqmine", "radix", "vips"]

runs = 3
def plot(ipath, opath, save):
	qps_data = []
	latency_data = []
	for i in range(runs):
		raw_latency, raw_qps = read_file(ipath, f'{i}_latency.txt')
		qps_data.append(np.array(raw_qps).mean(axis=0) / 1000)
		latency_data.append(np.array(raw_latency).mean(axis=0) / 1000)


	# ----------------------------------- Plotting -----------------------------------
	
	def plotA(ipath, opath, run, save):
		fig = plt.figure(1, figsize=(6, 8))
		# fig = plt.figure()
		ax = fig.add_subplot(111)

		ax.set_ylabel('95th Percentile Latency (ms)')
		ax1 = ax1.twinx()
		ax1.set_ylabel('QPS')

		lines, labels = ax.get_legend_handles_labels()
		lines1, labels1 = ax1.get_legend_handles_labels()
		lines.extend(lines1)
		labels.extend(labels1)

		ax.set_xlabel('Time (ms)')
		ax.grid(linestyle= '--')
		ax.legend(lines, labels, loc='lower right')
		ax.set_title("Plot {}A".format(run))

		if not save:
			plt.show()
		else:
			plt.savefig("{}/{}A.pdf".format(opath, run), bbox_inches='tight')
			plt.clf()

	def plotB(ipath, opath, run, save):
		fig = plt.figure(1, figsize=(6, 8))
		# fig = plt.figure()

		ax = fig.add_subplot(111)
		ax.set_ylabel('CPU core for Memcached')

		ax1 = ax1.twinx()
		ax1.set_ylabel('QPS')

		lines, labels = ax.get_legend_handles_labels()
		lines1, labels1 = ax1.get_legend_handles_labels()
		lines.extend(lines1)
		labels.extend(labels1)

		ax.set_xlabel('Time (s)')
		ax.grid(linestyle= '--')
		ax.legend(lines, labels, loc='lower right')
		ax.set_title("Plot {}B".format(run))

		if not save:
			plt.show()
		else:
			plt.savefig("{}/{}B.pdf".format(opath, run), bbox_inches='tight')
			plt.clf()

	def job_annotation(ipath, opath, run, save):
		for label, segs in zip(LABELS, time_segs):
			for seg in segs:
				ax.hlines(y=y, xmin=segment[0], xmax=segment[1], color='k')

		ax.set_yticks(range(len(LABELS)))
		ax.set_yticklabels(LABELS)

	for i in range(runs):
		plotA(ipath, opath, i, save)
		plotB(ipath, opath, i, save)

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("-i", "--input", help="Input data path", default="../data/part4_3")
	parser.add_argument("-s", "--save", help="Save plot", action="store_true")
	parser.add_argument("-o", "--output", help="Output data path", default="../data")
	args = parser.parse_args()

	plot(args.input, args.output, args.save)



