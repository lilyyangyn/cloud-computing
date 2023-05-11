import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter
import numpy as np
import argparse

def read_file(p, filename):
	raw_data = []
	real_qps = []

	trial_result = []
	trial_qps = []
	header = False
	with open(p + "/" + filename, 'r') as f:
		for line in f:
			if header:
				header = False
				continue
			if "End" in line:
				raw_data.append(trial_result)
				trial_result = []
				real_qps.append(trial_qps)
				trial_qps = []
				continue
			if "Start" in line:
				header = True
				continue
			data = line.split()
			if len(data) < 18:
				continue

			trial_result.append(float(data[12]))	# p95
			trial_qps.append(float(data[-2]))		# real qps

	return raw_data, real_qps

def plot(ipath, opath, save):
	raw_data_2_1, raw_qps_2_1 = np.array(read_file(ipath, "2_1.txt")) / 1000
	x_data_2_1 = raw_qps_2_1.mean(axis=0)
	y_data_2_1 = raw_data_2_1.mean(axis=0) 

	raw_data_2_2, raw_qps_2_2 = np.array(read_file(ipath, "2_2.txt")) / 1000
	x_data_2_2 = raw_qps_2_2.mean(axis=0)
	y_data_2_2 = raw_data_2_2.mean(axis=0) 
	# cpu_usage_2_1 *= 2

	# ----------------------------------- Plotting -----------------------------------

	# fig = plt.figure()

	fig, (ax1, ax2) = plt.subplots(nrows=1, ncols=2, figsize=(8, 4))

	ax1.plot(x_data_2_1, y_data_2_1, marker='o', label="95th perc. latency")
	ax1.set_ylabel('95th Percentile Latency (ms)')
	ax1.set_yticks(np.arange(0, 2.1, 0.2)) # 0 - 4ms

	ax1.axhline(y=1, linestyle="dotted", label="1ms latency SLO", color="grey")

	# ax1_1 = ax1.twinx()
	# ax1_1.plot(x_data_2_1, cpu_usage_2_1, marker='^', label="CPU Utilization")
	# ax1_1.set_ylabel('Average CPU Utilization (%)')
	# ax1_1.set_yticks(np.arange(0, 100, 20)) # 0 - 100

	ax2.axhline(y=1, linestyle="dotted", label="1ms latency SLO", color="grey")

	ax2.plot(x_data_2_2, y_data_2_2, marker='o', label="95th perc. latency")
	ax2.set_ylabel('95th Percentile Latency (ms)')
	ax2.set_yticks(np.arange(0, 2.1, 0.2)) # 0 - 4ms

	# ax2_1 = ax2.twinx()
	# ax2_1.plot(x_data_2_2, cpu_usage_2_2, marker='^', label="CPU Utilization")
	# ax2_1.set_ylabel('Average CPU Utilization (%)')
	# ax2_1.set_yticks(np.arange(0, 200, 20)) # 0 - 100

	ax1.xaxis.set_major_formatter(FormatStrFormatter('%dK'))
	ax1.set_xticks(np.arange(0, 125, 20)) # 0 - 125K
	ax1.set_xlabel('Queries per second (QPS)')
	ax1.grid(linestyle= '--')
	ax1.legend(loc='lower right')
	ax1.set_title("2 threads, 1 core\n(3 repetitions per points)")

	ax2.xaxis.set_major_formatter(FormatStrFormatter('%dK'))
	ax2.set_xticks(np.arange(0, 125, 20)) # 0 - 125K
	ax2.set_xlabel('Queries per second (QPS)')
	ax2.grid(linestyle= '--')
	ax2.legend(loc='lower right')
	ax2.set_title("2 threads, 2 cores\n(3 repetitions per points)")	
	
	if not save:
		plt.show()
	else:
		plt.savefig(opath+'/benchmark4_2.pdf', bbox_inches='tight')
		plt.clf()

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("-i", "--input", help="Input data path", default="data")
	parser.add_argument("-s", "--save", help="Save plot", action="store_true")
	parser.add_argument("-o", "--output", help="Output data path", default=".")
	args = parser.parse_args()

	plot(args.input, args.output, args.save)



