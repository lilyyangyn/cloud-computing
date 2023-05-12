#!/bin/bash

repeat=3
OUTPUT_FOLDER="data"

# ---------------------------- Script Starts ----------------------------

ZONE="europe-west3-a"
PROJECT="cca-eth-2023-group-49"

AGENT_INFO=$(kubectl get nodes -o wide | grep "client-agent-*")
AGENT_INTERNAL_NAME=$(echo ${AGENT_INFO} | awk '{print $1}')
AGENT_INTERNAL_IP=$(echo ${AGENT_INFO} | awk '{print $6}')
MEASURE_INFO=$(kubectl get nodes -o wide | grep "client-measure-*")
MEASURE_INTERNAL_NAME=$(echo ${MEASURE_INFO} | awk '{print $1}')
MEASURE_INTERNAL_IP=$(echo ${MEASURE_INFO} | awk '{print $6}')
MEMCACHED_IP=$(kubectl get nodes -o wide | grep "memcache-server-*" | awk '{print $6}')

# ---------------------------- Script YAML for Memcached ----------------------------

create_yaml() {
	threads_num=$1
	core_num=$2

	core_config="0"
	if [ ${core_num} = 2 ]; then
		core_config="0,1"
	fi

	echo """apiVersion: v1
kind: Pod
metadata:
  name: some-memcached
  labels:
    name: some-memcached
spec:
  containers:
    - image: anakli/memcached:t1
      name: memcached
      imagePullPolicy: Always
      command: [\"/bin/sh\"]
      args: [\"-c\", \"taskset -c ${core_config} ./memcached -t ${threads_num} -u memcache\"]
  nodeSelector:
    cca-project-nodetype: \"memcached\"
""" > memcache.yaml
}

# ---------------------------- Run Benchmarks ----------------------------
kubectl delete pods some-memcached 
kubectl delete service some-memcached-11211

# gcloud compute ssh --zone "europe-west3-a" "${AGENT_INTERNAL_NAME}"  --project "cca-eth-2023-group-49" \
# 	-- "cd mmemcache-perf-dynamic
# 		./mcperf -T 16 -A" &

gcloud compute ssh --zone "europe-west3-a" "${AGENT_INTERNAL_NAME}"  --project "cca-eth-2023-group-49" \
	-- "ps aux | grep memcached | awk '{print $2}' | sudo taskset -a -cp 0 '{print $1}'
		cd /home/ubuntu
		python3 cpu_util_measure.py" 

for threads in 1 2; do
	for cores in 1 2; do
		core_config="0"
		if [ ${core_num} = 2 ]; then
			core_config="0,1"
		fi

	# 	gcloud compute ssh --zone "europe-west3-a" "${AGENT_INTERNAL_NAME}"  --project "cca-eth-2023-group-49" \
	# -- "ps aux | grep memcached | awk '{print $2}' | sudo taskset -a -cp ${core_config} '{print $1}'
	# 	cd /home/ubuntu
	# 	python3 cpu_util_measure.py" > ${OUTPUT_FOLDER}/${threads}_${cores}_cpu.txt &

		gcloud compute ssh --zone ${ZONE} ${MEASURE_INTERNAL_NAME}  --project ${PROJECT} \
	-- "cd memcache-perf-dynamic
		repeat=${repeat}
		for (( i=1 ; i<=${repeat} ; i++ )); 
		do 
			echo "----- Start Round \$i -----" 
			./mcperf -s ${MEMCACHED_IP} --loadonly
			./mcperf -s ${MEMCACHED_IP} -a ${AGENT_INTERNAL_IP}  \
		           --noload -T 16 -C 4 -D 4 -Q 1000 -c 4 -t 5 \
				   --scan 5000:125000:5000
		    echo "----- End Round \$i -----"
		    sleep 2
		done" \
	| tee ${OUTPUT_FOLDER}/${threads}_${cores}.txt	# FIXME: sync error if not output to terminal

	sleep 60
	done
done

rm $memcache.yaml
