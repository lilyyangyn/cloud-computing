#!/bin/bash

repeat=5
OUTPUT_FOLDER="data"

# ---------------------------- Script Starts ----------------------------

ZONE="europe-west3-a"
PROJECT="cca-eth-2023-group-49"

AGENT_INFO=$(kubectl get nodes -o wide | grep "client-agent-*")
AGENT_INTERNAL_IP=$(echo ${AGENT_INFO} | awk '{print $6}')
MEASURE_INFO=$(kubectl get nodes -o wide | grep "client-measure-*")
MEASURE_INTERNAL_NAME=$(echo ${MEASURE_INFO} | awk '{print $1}')
MEASURE_INTERNAL_IP=$(echo ${MEASURE_INFO} | awk '{print $6}')

MEMCACHED_IP=$(kubectl get pod some-memcached --template '{{.status.podIP}}')

# ---------------------------- Start Test On Client Agent ----------------------------

# should only start once

# AGENT_INTERNAL_NAME=$(echo ${AGENT_INFO} | awk '{print $1}')

# gcloud compute ssh --zone "europe-west3-a" "${AGENT_INTERNAL_NAME}"  --project "cca-eth-2023-group-49" \
# 	-- "cd memcache-perf
# 		./mcperf -T 16 -A" &

# ---------------------------- Start Test On Client Measure ----------------------------	

# no-interference

gcloud compute ssh --zone ${ZONE} ${MEASURE_INTERNAL_NAME}  --project ${PROJECT} \
	-- "cd memcache-perf 
		repeat=${repeat}
		for (( i=1 ; i<=${repeat} ; i++ )); 
		do 
			echo "----- Start Round \$i -----" 
			./mcperf -s ${MEMCACHED_IP} --loadonly
			./mcperf -s ${MEMCACHED_IP} -a ${AGENT_INTERNAL_IP}  \
		           --noload -T 16 -C 4 -D 4 -Q 1000 -c 4 -w 2 -t 5 \
		           --scan 30000:110000:5000
		    echo "----- End Round \$i -----"
		    sleep 2
		done" \
	| tee ${OUTPUT_FOLDER}/no_interf.txt	# FIXME: sync error if not output to terminal

# interferences

for case in "cpu" "l1d" "l1i" "l2" "llc" "membw";
do
	sleep 30

	kubectl create -f interference/ibench-${case}.yaml
	sleep 60

	gcloud compute ssh --zone "${ZONE}" "${MEASURE_INTERNAL_NAME}"  --project "${PROJECT}" \
		-- "cd memcache-perf 
			repeat=${repeat}
			for (( i=1 ; i<=${repeat} ; i++ )); 
			do 
				echo "----- Start Round \$i -----" 
				./mcperf -s ${MEMCACHED_IP} --loadonly
				./mcperf -s ${MEMCACHED_IP} -a ${AGENT_INTERNAL_IP}  \
			           --noload -T 16 -C 4 -D 4 -Q 1000 -c 4 -w 2 -t 5 \
			           --scan 30000:110000:5000
			    echo "----- End Round \$i -----"
			    sleep 2
			done" \
		| tee ${OUTPUT_FOLDER}/${case}_interf.txt

	kubectl delete pods ibench-${case}
done


