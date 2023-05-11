import psutil

print("Start measurement of CPU utilization")
# with open("output.txt", "w") as f:
# 	for i in range(50):
# 		util = psutil.cpu_percent(interval=5, percpu=True)
# 		print("round", i, ":", util)
# 	    f.write(util, "\n")

for i in range(50):
	print(psutil.cpu_percent(interval=5, percpu=True))


