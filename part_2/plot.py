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
	raw_data_1, _ = np.array(read_file(ipath, "no_interf.txt")) / 1000
	base_raw = raw_data_1
	base = raw_data_1.mean(axis=0)
	y_data_1 = np.ones(4)
	y_err_1 = np.zeros(4)

	raw_data_2, _ = np.array(read_file(ipath, "2_interf.txt")) / 1000
	y_data_2 = base / raw_data_2.mean(axis=0) 
	y_err_2 = np.std(base_raw/raw_data_2, axis=0, ddof=0) / np.sqrt(len(raw_data_2))

	raw_data_4, _ = np.array(read_file(ipath, "4_interf.txt")) / 1000
	y_data_4 = base / raw_data_4.mean(axis=0) 
	y_err_4 = np.std(base_raw/raw_data_4, ddof=1) / np.sqrt(len(raw_data_4))

	raw_data_8, _ = np.array(read_file(ipath, "8_interf.txt")) / 1000
	y_data_8 = base / raw_data_8.mean(axis=0) 
	y_err_8 = np.std(base_raw/raw_data_8, ddof=1) / np.sqrt(len(raw_data_8))

	x_data = [ 1, 2, 4, 8 ]

	# ----------------------------------- Plotting -----------------------------------

	plt.errorbar(x_data_1, y_data_1, xerr=x_err_1, yerr=y_err_1, fmt='-o', markersize=10, markerfacecolor='None', capsize=3, label="no interference")
	plt.errorbar(x_data_2, y_data_2, xerr=x_err_2, yerr=y_err_2, fmt='-s', markersize=10, markerfacecolor='None', capsize=3, label="interference on 2")
	plt.errorbar(x_data_4, y_data_4, xerr=x_err_4, yerr=y_err_4, fmt='-x', markersize=10, markerfacecolor='None', capsize=3, label="interference on 4")
	plt.errorbar(x_data_8, y_data_8, xerr=x_err_8, yerr=y_err_8, fmt='-<', markersize=10, markerfacecolor='None', capsize=3, label="interference on 8")
	
	plt.xticks(np.arange(0, 9, 1))	# 0 - 8
	plt.yticks(np.arange(0, 1, 0.0.5))	# 0 - 1

	plt.xlabel('Number of threads')
	plt.ylabel('Speedup (Time$_1$/Timen$_n$)')

	plt.grid(linestyle= '--')

	plt.legend(loc='center right', bbox_to_anchor=(1.5, 0.5))

	plt.title("Speedup using different number of threads\nError bar: 1. (5 repetitions per points)")
	# plt.gca().set_aspect("equal")

	if not save:
		plt.show()
	else:
		plt.savefig(opath+'/benchmark.pdf', bbox_inches='tight')
		plt.clf()

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("-i", "--input", help="Input data path", default="data")
	parser.add_argument("-s", "--save", help="Save plot", action="store_true")
	parser.add_argument("-o", "--output", help="Output data path", default=".")
	args = parser.parse_args()

	plot(args.input, args.output, args.save)

