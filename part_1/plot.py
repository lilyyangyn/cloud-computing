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
	raw_data_nil, raw_qps_nil = np.array(read_file(ipath, "no_interf.txt")) / 1000
	x_data_nil = raw_qps_nil.mean(axis=0)
	x_err_nil = np.std(raw_qps_nil, axis=0, ddof=0) / np.sqrt(len(raw_qps_nil))
	y_data_nil = raw_data_nil.mean(axis=0) 
	y_err_nil = np.std(raw_data_nil, axis=0, ddof=0) / np.sqrt(len(raw_data_nil))

	raw_data_cpu, raw_qps_cpu = np.array(read_file(ipath, "cpu_interf.txt")) / 1000
	x_data_cpu = raw_qps_cpu.mean(axis=0)
	x_err_cpu = np.std(raw_qps_cpu, axis=0, ddof=0) / np.sqrt(len(raw_qps_cpu))
	y_data_cpu = raw_data_cpu.mean(axis=0) 
	y_err_cpu = np.std(raw_data_cpu, axis=0, ddof=0) / np.sqrt(len(raw_data_cpu))

	raw_data_l1d, raw_qps_l1d = np.array(read_file(ipath, "l1d_interf.txt")) / 1000
	x_data_l1d = raw_qps_l1d.mean(axis=0)
	x_err_l1d = np.std(raw_qps_l1d, axis=0, ddof=0) / np.sqrt(len(raw_qps_l1d))
	y_data_l1d = raw_data_l1d.mean(axis=0) 
	y_err_l1d = np.std(raw_data_l1d, ddof=1) / np.sqrt(len(raw_data_l1d))

	raw_data_l1i, raw_qps_l1i = np.array(read_file(ipath, "l1i_interf.txt")) / 1000
	x_data_l1i = raw_qps_l1i.mean(axis=0)
	x_err_l1i = np.std(raw_qps_l1i, axis=0, ddof=0) / np.sqrt(len(raw_qps_l1i))
	y_data_l1i = raw_data_l1i.mean(axis=0) 
	y_err_l1i = np.std(raw_data_l1i, ddof=1) / np.sqrt(len(raw_data_l1i))

	raw_data_l2, raw_qps_l2 = np.array(read_file(ipath, "l2_interf.txt")) / 1000
	x_data_l2 = raw_qps_l2.mean(axis=0)
	x_err_l2 = np.std(raw_qps_l2, axis=0, ddof=0) / np.sqrt(len(raw_qps_l2))
	y_data_l2 = raw_data_l2.mean(axis=0)
	y_err_l2 = np.std(raw_data_l2, ddof=1) / np.sqrt(len(raw_data_l2))

	raw_data_llc, raw_qps_llc = np.array(read_file(ipath, "llc_interf.txt")) / 1000
	x_data_llc = raw_qps_llc.mean(axis=0)
	x_err_llc = np.std(raw_qps_llc, axis=0, ddof=0) / np.sqrt(len(raw_qps_llc))
	y_data_llc = raw_data_llc.mean(axis=0)
	y_err_llc = np.std(raw_data_llc, ddof=1) / np.sqrt(len(raw_data_llc))

	raw_data_membw, raw_qps_membw = np.array(read_file(ipath, "membw_interf.txt")) / 1000
	x_data_membw = raw_qps_membw.mean(axis=0)
	x_err_membw = np.std(raw_qps_membw, axis=0, ddof=0) / np.sqrt(len(raw_qps_membw))
	y_data_membw = raw_data_membw.mean(axis=0)
	y_err_membw = np.std(raw_data_membw, ddof=1) / np.sqrt(len(raw_data_membw))

	# x_data = [ x for x in range(30, 111, 5) ]

	# ----------------------------------- Plotting -----------------------------------

	plt.errorbar(x_data_nil, y_data_nil, xerr=x_err_nil, yerr=y_err_nil, fmt='-o', markersize=10, markerfacecolor='None', capsize=3, label="no interference")
	plt.errorbar(x_data_cpu, y_data_cpu, xerr=x_err_cpu, yerr=y_err_cpu, fmt='-s', markersize=10, markerfacecolor='None', capsize=3, label="interference on cpu")
	plt.errorbar(x_data_l1d, y_data_l1d, xerr=x_err_l1d, yerr=y_err_l1d, fmt='-x', markersize=10, markerfacecolor='None', capsize=3, label="interference on l1d")
	plt.errorbar(x_data_l1i, y_data_l1i, xerr=x_err_l1i, yerr=y_err_l1i, fmt='-<', markersize=10, markerfacecolor='None', capsize=3, label="interference on l1i")
	plt.errorbar(x_data_l2, y_data_l2, xerr=x_err_l2, yerr=y_err_l2, fmt='-v', markersize=10, markerfacecolor='None', capsize=3, label="interference on l2")
	plt.errorbar(x_data_llc, y_data_llc, xerr=x_err_llc, yerr=y_err_llc, fmt='-^', markersize=10, markerfacecolor='None', capsize=3, label="interference on llc")
	plt.errorbar(x_data_membw, y_data_membw, xerr=x_err_membw, yerr=y_err_membw, fmt='>', markersize=10, markerfacecolor='None', capsize=3, label="interference on membw")

	# plt.xlim([0, 115])		
	# plt.ylim([0, 8])		
	plt.xticks(np.arange(0, 111, 10))	# 0 - 110K
	plt.yticks(np.arange(0, 8.5, 0.5))	# 0 - 8ms


	plt.gca().xaxis.set_major_formatter(FormatStrFormatter('%dK'))

	plt.xlabel('Queries per second (QPS)')
	plt.ylabel('95th Latency (ms)')

	plt.grid(linestyle= '--')

	plt.legend(loc='center right', bbox_to_anchor=(1.5, 0.5))

	plt.title("95th Latency with different loads and interferences\nError bar: 1ms. (5 repetitions per points)")
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



