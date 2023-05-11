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
	raw_data_1_1, raw_qps_1_1 = np.array(read_file(ipath, "1_1.txt")) / 1000
	x_data_1_1 = raw_qps_1_1.mean(axis=0)
	x_err_1_1 = np.std(raw_qps_1_1, axis=0, ddof=0) / np.sqrt(len(raw_qps_1_1))
	y_data_1_1 = raw_data_1_1.mean(axis=0) 
	y_err_1_1 = np.std(raw_data_1_1, axis=0, ddof=0) / np.sqrt(len(raw_data_1_1))

	raw_data_1_2, raw_qps_1_2 = np.array(read_file(ipath, "1_2.txt")) / 1000
	x_data_1_2 = raw_qps_1_2.mean(axis=0)
	x_err_1_2 = np.std(raw_qps_1_2, axis=0, ddof=0) / np.sqrt(len(raw_qps_1_2))
	y_data_1_2 = raw_data_1_2.mean(axis=0) 
	y_err_1_2 = np.std(raw_data_1_2, axis=0, ddof=0) / np.sqrt(len(raw_data_1_2))

	raw_data_2_1, raw_qps_2_1 = np.array(read_file(ipath, "2_1.txt")) / 1000
	x_data_2_1 = raw_qps_2_1.mean(axis=0)
	x_err_2_1 = np.std(raw_qps_2_1, axis=0, ddof=0) / np.sqrt(len(raw_qps_2_1))
	y_data_2_1 = raw_data_2_1.mean(axis=0) 
	y_err_2_1 = np.std(raw_data_2_1, ddof=1) / np.sqrt(len(raw_data_2_1))

	raw_data_2_2, raw_qps_2_2 = np.array(read_file(ipath, "2_2.txt")) / 1000
	x_data_2_2 = raw_qps_2_2.mean(axis=0)
	x_err_2_2 = np.std(raw_qps_2_2, axis=0, ddof=0) / np.sqrt(len(raw_qps_2_2))
	y_data_2_2 = raw_data_2_2.mean(axis=0) 
	y_err_2_2 = np.std(raw_data_2_2, ddof=1) / np.sqrt(len(raw_data_2_2))

	# ----------------------------------- Plotting -----------------------------------

	fig = plt.figure(1, figsize=(6, 8))
	# fig = plt.figure()
	ax = fig.add_subplot(111)

	ax.errorbar(x_data_1_1, y_data_1_1, xerr=x_err_1_1, yerr=y_err_1_1, fmt='-o', markerfacecolor='None', capsize=3, label="1 thread, 1 core")
	ax.errorbar(x_data_1_2, y_data_1_2, xerr=x_err_1_2, yerr=y_err_1_2, fmt='-s', markerfacecolor='None', capsize=3, label="1 thread, 2 cores")
	ax.errorbar(x_data_2_1, y_data_2_1, xerr=x_err_2_1, yerr=y_err_2_1, fmt='-x', markerfacecolor='None', capsize=3, label="2 threads, 1 core")
	ax.errorbar(x_data_2_2, y_data_2_2, xerr=x_err_2_2, yerr=y_err_2_2, fmt='-<', markerfacecolor='None', capsize=3, label="2 threads, 2 cores")

	plt.xlim([0, 110])		
	plt.ylim([0, 2.4])		
	ax.set_xticks(np.arange(0, 131, 10))	# 0 - 125K
	ax.set_yticks(np.arange(0, 2.5, 0.2))	# 0 - 8ms

	ax.xaxis.set_major_formatter(FormatStrFormatter('%dK'))

	ax.set_xlabel('Queries per second (QPS)')
	ax.set_ylabel('95th Latency (ms)')

	ax.grid(linestyle= '--')

	# ax.legend(loc='center right', bbox_to_anchor=(1.5, 0.5))
	ax.legend(loc='upper left')

	ax.set_title("95th Latency with different loads and interferences\nError bar: 1ms. (3 repetitions per points)")
	
	if not save:
		plt.show()
	else:
		plt.savefig(opath+'/benchmark4_1.pdf', bbox_inches='tight')
		plt.clf()

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("-i", "--input", help="Input data path", default="data")
	parser.add_argument("-s", "--save", help="Save plot", action="store_true")
	parser.add_argument("-o", "--output", help="Output data path", default=".")
	args = parser.parse_args()

	plot(args.input, args.output, args.save)



