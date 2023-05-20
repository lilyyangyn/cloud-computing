from datetime import datetime
import numpy as np

def read_file_logs(p, filename):
	times = []
	logs = {}
	with open(p + "/" + filename, 'r') as f:
		for line in f:
			data = line.split()
			if len(data) < 3:
				continue

			subject = data[2]
			if subject == "scheduler":
				times.append(datetime.strptime(data[0], '%Y-%m-%dT%H:%M:%S.%f').timestamp())
				continue
			if subject == "memcached":
				continue

			if subject not in logs:
				logs[data[2]] = []

			time = datetime.strptime(data[0], '%Y-%m-%dT%H:%M:%S.%f').timestamp()
			if data[1] == "start" or data[1] == "unpause":
				logs[data[2]].append([time])
			elif data[1] == "pause" or data[1] == "end":
				logs[data[2]][-1].append(time)

	return times, logs

def read_file_latency(p, filename, threshold, start, end):
	count = 0
	header = True
	interval = 0
	interval_num = 0
	total = 0
	start_time = 0
	with open(p + "/" + filename, 'r') as f:
		for line in f:
			if "Total number of intervals" in line:
				interval_num = float(line.split()[5])
				continue
			if "Timestamp start" in line:
				start_time = float(line.split()[-1])/1000
				continue
			if "Timestamp end" in line:
				end_time = float(line.split()[-1])/1000
				interval = (end_time - start_time) / interval_num
				continue

			data = line.split()
			if len(data) != 18:
				continue

			if header:
				header = False
				continue

			if start_time > start:
				total += 1
				latency = float(data[12])
				if latency > threshold:
					count += 1
				if start_time > end:
					break
			start_time += interval
	return count / total

if __name__ == "__main__":
	path = "../data/part4_4/1s"

	violations = []
	running_time = []
	for i in range(3):
		times, logs = read_file_logs(path, f'jobs_{i+1}.txt')
		violations.append(read_file_latency(path, f'mcperf_{i+1}.txt', 1000, times[0], times[1]))
		
		runtime = []
		for job in logs:
			total = 0
			for seg in logs[job]:
				total += seg[1] - seg[0] 
			print(job, total)
			runtime.append(total)
		runtime.append(times[1]-times[0])
		running_time.append(runtime)
		print()

	print("slo violation:", violations)

	jobs = " ".join([job for job in logs] + ["all"])

	data = np.array(running_time)
	print(jobs)
	print("mean:", np.mean(data, axis=0))
	print("std:", np.std(data, axis=0))




