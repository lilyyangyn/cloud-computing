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
# 	-- "cd memcache-perf
# 		./mcperf -T 16 -A" &

for threads in 1 2; do
	for cores in 1 2; do
		create_yaml ${threads} ${cores}
		kubectl create -f memcache.yaml
		kubectl expose pod some-memcached --name some-memcached-11211  \
                                    --type LoadBalancer --port 11211 \
                                    --protocol TCP
		sleep 60
		kubectl get service some-memcached-11211

		memcache_ip=$(kubectl get pod some-memcached --template '{{.status.podIP}}')

		gcloud compute ssh --zone ${ZONE} ${MEASURE_INTERNAL_NAME}  --project ${PROJECT} \
	-- "cd memcache-perf 
		repeat=${repeat}
		for (( i=1 ; i<=${repeat} ; i++ )); 
		do 
			echo "----- Start Round \$i -----" 
			./mcperf -s ${memcache_ip} --loadonly
			./mcperf -s ${memcache_ip} -a ${AGENT_INTERNAL_IP}  \
		           --noload -T 16 -C 4 -D 4 -Q 1000 -c 4 -t 5 \
				   --scan 5000:125000:5000
		    echo "----- End Round \$i -----"
		    sleep 2
		done" \
	| tee ${OUTPUT_FOLDER}/${threads}_${cores}.txt	# FIXME: sync error if not output to terminal

	kubectl delete pods some-memcached 
	kubectl delete service some-memcached-11211

	sleep 60
	done
done

rm $memcache.yaml
