#!/bin/bash

repeat=5

# ---------------------------- Script Starts ----------------------------

ZONE="europe-west3-a"
PROJECT="cca-eth-2023-group-49"

# AGENT_INTERNAL_NAME=$(kubectl get nodes -o wide | grep "client-agent-*" | awk '{print $1}')
AGENT_INTERNAL_IP=$(kubectl get nodes -o wide | grep "client-agent-*" | awk '{print $6}')
MEASURE_INTERNAL_NAME=$(kubectl get nodes -o wide | grep "client-measure-*" | awk '{print $1}')
MEASURE_INTERNAL_IP=$(kubectl get nodes -o wide | grep "client-measure-*" | awk '{print $6}')

echo $AGENT_INTERNAL_IP

# no-interference

MEMCACHED_IP=$(kubectl get pod some-memcached --template '{{.status.podIP}}')

gcloud compute ssh --zone ${ZONE} ${MEASURE_INTERNAL_NAME}  --project ${PROJECT} \
	-- "cd memcache-perf 
		repeat=${repeat}
		for (( i=1 ; i<=${repeat} ; i++ )); 
		do 
			echo "----- Start ROUDN $i -----" 
			./mcperf -s ${MEMCACHED_IP} --loadonly
			./mcperf -s ${MEMCACHED_IP} -a ${AGENT_INTERNAL_IP}  \
		           --noload -T 16 -C 4 -D 4 -Q 1000 -c 4 -w 2 -t 5 \
		           --scan 30000:110000:5000
		    echo "----- End ROUDN $i -----"
		    sleep 2
		done" \
	| tee output/interference_nil.txt	# FIXME: sync error if not output to terminal

# interferences

for case in "cpu" "l1d" "l1i" "l2" "llc" "membw"
do
	sleep 30

	kubectl create -f interference/ibench-${case}.yaml
	sleep 60

	MEMCACHED_IP=$(kubectl get pod ibench-${case} --template '{{.status.podIP}}')
	echo $MEMCACHED_IP

	gcloud compute ssh --zone "${ZONE}" "${MEASURE_INTERNAL_NAME}"  --project "${PROJECT}" \
		-- "cd memcache-perf 
			repeat=${repeat}
			for (( i=1 ; i<=${repeat} ; i++ )); 
			do 
				echo "----- Start ROUDN $i -----" 
				./mcperf -s ${MEMCACHED_IP} --loadonly
				./mcperf -s ${MEMCACHED_IP} -a ${AGENT_INTERNAL_IP}  \
			           --noload -T 16 -C 4 -D 4 -Q 1000 -c 4 -w 2 -t 5 \
			           --scan 30000:110000:5000
			    echo "----- End ROUDN $i -----"
			    sleep 2
			done" \
		| tee output/interference_${case}.txt

	kubectl delete pods ibench-${case}
	break
done


