import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter
import numpy as np
import argparse
from util import *


def plot(ipath, opath, save):
	raw_data_2_1, raw_qps_2_1, start_times_2_1 = read_file_latency(ipath, "2_1_latency.txt")
	x_data_2_1 = np.array(raw_qps_2_1).mean(axis=0)/1000
	y_data_2_1 = np.array(raw_data_2_1).mean(axis=0)/1000

	raw_data_2_2, raw_qps_2_2, start_times_2_2 = read_file_latency(ipath, "2_2_latency.txt")
	x_data_2_2 = np.array(raw_qps_2_2).mean(axis=0) / 1000
	y_data_2_2 = np.array(raw_data_2_2).mean(axis=0) / 1000

	cpu_2_1_temp = np.array(read_file_cpu(ipath, "2_1_cpu.txt", start_times_2_1, 1))[0]
	cpu_2_1 = np.apply_along_axis(lambda x: np.sum(x.reshape(-1, 5), axis=1)/5, 0, 
				cpu_2_1_temp[0])
	cpu_2_2_temp = np.array(read_file_cpu(ipath, "2_2_cpu.txt", start_times_2_2, 2))[0]
	cpu_2_2 = np.apply_along_axis(lambda x: np.sum(x.reshape(-1, 5), axis=1)/5, 0, np.sum(cpu_2_2_temp, axis=0))
	# print(cpu_2_1_temp)

	# ----------------------------------- Plotting -----------------------------------

	# fig = plt.figure()

	fig, (ax1, ax2) = plt.subplots(nrows=1, ncols=2, figsize=(13, 6))
	fig.subplots_adjust(wspace=0.4)

	ax1.axhline(y=1, linestyle="dotted", label="1ms latency SLO", color="grey")

	ax1.plot(x_data_2_1, y_data_2_1, marker='o', label="95th perc. latency")
	ax1.set_ylabel('95th Percentile Latency (ms)')
	ax1.set_yticks(np.arange(0, 2.1, 0.2)) # 0 - 4ms
	# ax1.yaxis.label.set_color('blue')
	ax1.tick_params(axis='y', labelcolor='tab:blue', labelsize=12)

	ax1_1 = ax1.twinx()
	ax1_1.plot(x_data_2_1, cpu_2_1, marker='^', label="CPU Utilization", color="orange")
	ax1_1.set_ylabel('Average CPU Utilization (%)')
	ax1_1.set_ylim([0, 101])
	ax1_1.set_yticks(np.arange(0, 120, 20)) # 0 - 100
	ax1_1.tick_params(axis='y', labelcolor='tab:orange', labelsize=12)

	lines1, labels1 = ax1.get_legend_handles_labels()
	lines1_2, labels1_2 = ax1_1.get_legend_handles_labels()
	lines1.extend(lines1_2)
	labels1.extend(labels1_2)

	ax2.axhline(y=1, linestyle="dotted", label="1ms latency SLO", color="grey")

	ax2.plot(x_data_2_2, y_data_2_2, marker='o', label="95th perc. latency")
	ax2.set_ylabel('95th Percentile Latency (ms)')
	ax2.set_yticks(np.arange(0, 2.1, 0.2)) # 0 - 4ms
	ax2.tick_params(axis='y', labelcolor='tab:blue', labelsize=12)

	ax2_1 = ax2.twinx()
	ax2_1.plot(x_data_2_2, cpu_2_2, marker='^', label="CPU Utilization", color="orange")
	ax2_1.set_ylabel('Average CPU Utilization (%)')
	ax2_1.set_ylim([0, 201],)
	ax2_1.set_yticks(np.arange(0, 220, 20)) # 0 - 100
	ax2_1.tick_params(axis='y', labelcolor='tab:orange', labelsize=12)

	lines2, labels2 = ax2.get_legend_handles_labels()
	lines2_2, labels2_2 = ax2_1.get_legend_handles_labels()
	lines2.extend(lines2_2)
	labels2.extend(labels2_2)

	ax1.xaxis.set_major_formatter(FormatStrFormatter('%dK'))
	ax1.set_xticks(np.arange(0, 125, 20)) # 0 - 125K
	ax1.set_xlabel('Queries per second (QPS)')
	ax1.grid(linestyle= '--')
	ax1.legend(lines1, labels1, loc='lower right')
	ax1.set_title("2 threads, 1 core\n(3 repetitions per points)")

	ax2.xaxis.set_major_formatter(FormatStrFormatter('%dK'))
	ax2.set_xticks(np.arange(0, 125, 20)) # 0 - 125K
	ax2.set_xlabel('Queries per second (QPS)')
	ax2.grid(linestyle= '--')
	ax2.legend(lines2, labels2, loc='lower right')
	ax2.set_title("2 threads, 2 cores\n(3 repetitions per points)")	
	
	if not save:
		plt.show()
	else:
		plt.savefig(opath+'/benchmark4_2.pdf', bbox_inches='tight')
		plt.clf()

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("-i", "--input", help="Input data path", default="../data/part4_2")
	parser.add_argument("-s", "--save", help="Save plot", action="store_true")
	parser.add_argument("-o", "--output", help="Output data path", default="../data")
	args = parser.parse_args()

	plot(args.input, args.output, args.save)



