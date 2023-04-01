import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter
import numpy as np
import argparse

def string_to_sec(str):
	strs = str[:-1].split('m')
	if len(strs) > 2:
		raise Exception("Wrong time string")
	secs = float(strs[-1])
	if len(strs) == 2:
		secs += float(strs[-2]) * 60

	return secs


def read_file(p, filename):
	raw_data = []

	trial_result = []
	init = False
	with open(p + "/" + filename, 'r') as f:
		for line in f:
			if "Threads NUM" in line:
				if not init:
					init = True
					continue
				raw_data.append(trial_result)
				trial_result = []
				continue
			data = line.split()
			if len(data) < 4:
				continue
			duration = string_to_sec(data[2])
			trial_result.append(duration)	
	raw_data.append(trial_result)

	return raw_data

def plot(ipath, opath, save):
	error_bar_base = 2

	raw_data_blackscholes = np.array(read_file(ipath, "blackscholes.txt")) 
	blackscholes_mean = raw_data_blackscholes.mean(axis=1)
	y_data_blackscholes = blackscholes_mean[0]/blackscholes_mean
	y_err_blackscholes = np.std(raw_data_blackscholes, axis=1, ddof=0) / np.sqrt(len(raw_data_blackscholes)) / error_bar_base
	
	raw_data_canneal = np.array(read_file(ipath, "canneal.txt")) 
	canneal_mean = raw_data_canneal.mean(axis=1)
	y_data_canneal = canneal_mean[0]/canneal_mean
	y_err_canneal = np.std(raw_data_canneal, axis=1, ddof=0) / np.sqrt(len(raw_data_canneal)) / error_bar_base

	raw_data_dedup = np.array(read_file(ipath, "dedup.txt")) 
	dedup_mean = raw_data_dedup.mean(axis=1)
	y_data_dedup = dedup_mean[0]/dedup_mean
	y_err_dedup = np.std(raw_data_dedup, axis=1, ddof=0) / np.sqrt(len(raw_data_dedup)) / error_bar_base

	raw_data_ferret = np.array(read_file(ipath, "ferret.txt")) 
	ferret_mean = raw_data_ferret.mean(axis=1)
	y_data_ferret = ferret_mean[0]/ferret_mean
	y_err_ferret = np.std(raw_data_ferret, axis=1, ddof=0) / np.sqrt(len(raw_data_ferret)) / error_bar_base

	raw_data_freqmine = np.array(read_file(ipath, "freqmine.txt")) 
	freqmine_mean = raw_data_freqmine.mean(axis=1)
	y_data_freqmine = freqmine_mean[0]/freqmine_mean
	y_err_freqmine = np.std(raw_data_freqmine, axis=1, ddof=0) / np.sqrt(len(raw_data_freqmine)) / error_bar_base

	raw_data_radix = np.array(read_file(ipath, "radix.txt")) 
	radix_mean = raw_data_radix.mean(axis=1)
	y_data_radix = radix_mean[0]/radix_mean
	y_err_radix = np.std(raw_data_radix, axis=1, ddof=0) / np.sqrt(len(raw_data_radix)) / error_bar_base

	raw_data_vips = np.array(read_file(ipath, "vips.txt")) 
	vips_mean = raw_data_vips.mean(axis=1)
	y_data_vips = vips_mean[0]/vips_mean
	y_err_vips = np.std(raw_data_vips, axis=1, ddof=0) / np.sqrt(len(raw_data_vips)) / error_bar_base

	x_data = [ 1, 2, 4, 8 ]

	# ----------------------------------- Plotting -----------------------------------

	plt.errorbar(x_data, y_data_blackscholes, yerr=y_err_blackscholes, fmt='-o', markerfacecolor='None', capsize=3, label="blackscholes")
	plt.errorbar(x_data, y_data_canneal, yerr=y_err_canneal, fmt='-s', markerfacecolor='None', capsize=3, label="canneal")
	plt.errorbar(x_data, y_data_dedup, yerr=y_err_dedup, fmt='-x', markerfacecolor='None', capsize=3, label="dedup")
	plt.errorbar(x_data, y_data_ferret, yerr=y_err_ferret, fmt='-<', markerfacecolor='None', capsize=3, label="ferret")
	plt.errorbar(x_data, y_data_freqmine, yerr=y_err_freqmine, fmt='-v', markerfacecolor='None', capsize=3, label="freqmine")
	plt.errorbar(x_data, y_data_radix, yerr=y_err_radix, fmt='-^', markerfacecolor='None', capsize=3, label="radix")
	plt.errorbar(x_data, y_data_vips, yerr=y_err_vips, fmt='->', markerfacecolor='None', capsize=3, label="vips")
	
	x = np.linspace(0,5,100)
	y = x
	plt.plot(x, y, linestyle="--", label="linear scalability")

	plt.xlim([0, 8.5])	
	plt.ylim([0, 5])	
	plt.xticks(np.arange(0, 8.5, 1))		# 0 - 8
	plt.yticks(np.arange(0, 5, 0.5))		# 0 - 3

	plt.xlabel('Number of threads')
	plt.ylabel('Speedup (Time$_1$/Timen$_n$)')

	plt.grid(linestyle= '--')

	plt.legend(loc='center right', bbox_to_anchor=(1.35, 0.5))

	plt.title("Speedup of different jobs v.s. Number of threads\nError bar: 2s. (3 repetitions per points)")
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

