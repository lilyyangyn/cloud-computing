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
			trial_qps.append(float(data[16]))		# real qps

	return raw_data, real_qps

def read_file_latency(p, filename):
	raw_data = []
	real_qps = []
	start_times = []

	trial_result = []
	trial_qps = []
	start_time = []
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
				start_times.append(start_time)
				start_time = []
				continue
			if "Start" in line:
				header = True
				continue
			data = line.split()
			if len(data) < 18:
				continue

			trial_result.append(float(data[12]))	# p95
			trial_qps.append(float(data[16]))		# real qps
			start_time.append(data[-2][:-3])	# start time

	return raw_data, real_qps, start_times

def read_file_cpu(p, filename, start_times, cores):
	utilizations = []

	tests = []
	for i in range(cores):
		tests.append([])
	counter = 0
	round_id = 0
	with open(p + "/" + filename, 'r') as f:
		for line in f:
			if "End" in line:
				utilizations.append(tests)
				tests = []
				for i in range(cores):
					tests.append([])
				round_id += 1
				continue
			if "Start" in line:
				continue

			data = line.split("[")
			if counter == 0:
				start_time = data[0].split(".")[0]
				if start_time in start_times[round_id]:
					counter = 5
				else:
					continue

			values = data[-1].strip("]").split(",")
			
			if len(values) < cores:
				continue

			for i in range(cores):
				tests[i].append(float(values[i]))
			counter -= 1

	return utilizations