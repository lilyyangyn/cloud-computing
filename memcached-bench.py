import matplotlib.pyplot as plt
import numpy as np

raw_data_nil = np.array([
	[],
	[],
	[],
	])
y_data_nil = raw_data_nil.mean(axis=0)

raw_data_cpu = np.array([
	[],
	[],
	[],
	])
y_data_cpu = raw_data_cpu.mean(axis=0)

raw_data_lid = np.array([
	[],
	[],
	[],
	])
y_data_l1d = raw_data_lid.mean(axis=0)

raw_data_l1i = np.array([
	[],
	[],
	[],
	])
y_data_l1i = raw_data_l1i.mean(axis=0)

raw_data_l2 = np.array([
	[],
	[],
	[],
	])
y_data_l2 = raw_data_l2.mean(axis=0)

raw_data_llc = np.array([
	[],
	[],
	[],
	])
y_data_llc = raw_data_llc.mean(axis=0)

raw_data_membw = np.array([
	[],
	[],
	[],
	])
y_data_membw = raw_data_membw.mean(axis=0)

x_data = [ x for x in range(30000, 110000, 5000) ]

# ----------------------------------- Plotting -----------------------------------

# plots
plt.plot(x_data, y_data_nil, label="no interference")
plt.plot(x_data, y_data_cpu, label="interference on cpu")
plt.plot(x_data, y_data_l1c, label="interference on l1c")
plt.plot(x_data, y_data_l1i, label="interference on l1i")
plt.plot(x_data, y_data_l2, label="interference on l2")
plt.plot(x_data, y_data_llc, label="interference on llc")
plt.plot(x_data, y_data_membw, label="interference on membw")

# error bars

# matplotlib.pyplot.errorbar(x, y, yerr=None, xerr=None, fmt='', ecolor=None, elinewidth=None, capsize=None, barsabove=False, lolims=False, uplims=False, xlolims=False, xuplims=False, errorevery=1, capthick=None, *, data=None, **kwargs)[source]

# plt.errorbar()


plt.xlim([0, 80000])	# 0 - 80K
plt.ylim([0, 8])		# 0 - 8ms

plt.xlabel('Queries per second (QPS)')
plt.xlabel('Latency (ms)')

plt.legend(loc='upper right')

./mcperf -s 100.70.121.160 -a 10.0.16.4  \
           --noload -T 16 -C 4 -D 4 -Q 1000 -c 4 -w 2 -t 5 \
           --scan 30000:110000:5000

