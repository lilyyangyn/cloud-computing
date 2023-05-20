#!/bin/bash

ethzid="yuening"

# ---------------------------- Script Starts ----------------------------

gsutil mb gs://cca-eth-2023-group-49-${ethzid}/
export KOPS_STATE_STORE=gs://cca-eth-2023-group-49-${ethzid}/
kops delete cluster part4.k8s.local --yes

PROJECT=`gcloud config get-value project`
kops create -f ../setup-config/part4.yaml
kops create secret --name part4.k8s.local sshpublickey admin -i ~/.ssh/cloud-computing.pub
kops update cluster --name part4.k8s.local --yes --admin
sleep 60
kops validate cluster --wait 10m

# ---------------------------- Running memcached and the mcperf load generator ----------------------------

MEMCACHED_SERVER_NAME=$(kubectl get nodes -o wide | grep "memcache-server-*" | awk '{print $1}')
AGENT_INTERNAL_NAME=$(kubectl get nodes -o wide | grep "client-agent-*" | awk '{print $1}')
# AGENT_INTERNAL_IP=$(kubectl get nodes -o wide | grep "client-agent-*" | awk '{print $6}')
MEASURE_INTERNAL_NAME=$(kubectl get nodes -o wide | grep "client-measure-*" | awk '{print $1}')
# MEASURE_INTERNAL_IP=$(kubectl get nodes -o wide | grep "client-measure-*" | awk '{print $6}')

gcloud compute ssh --zone "europe-west3-a" "${AGENT_INTERNAL_NAME}"  --project "cca-eth-2023-group-49" \
	-- "sudo apt-get update
		sudo apt-get install libevent-dev libzmq3-dev git make g++ --yes
		sudo apt-get build-dep memcached --yes
		git clone https://github.com/eth-easl/memcache-perf-dynamic.git
		cd memcache-perf-dynamic
		make" 

gcloud compute ssh --zone "europe-west3-a" "${MEASURE_INTERNAL_NAME}"  --project "cca-eth-2023-group-49" \
	-- "sudo apt-get update
		sudo apt-get install libevent-dev libzmq3-dev git make g++ --yes
		sudo apt-get build-dep memcached --yes
		git clone https://github.com/eth-easl/memcache-perf-dynamic.git
		cd memcache-perf-dynamic
		make" 

gcloud compute scp --scp-flag=-r cpu_util_measure.py ubuntu@${MEMCACHED_SERVER_NAME}:/home/ubuntu/ --zone europe-west3-a
gcloud compute scp --scp-flag=-r memcached_config.txt ubuntu@${MEMCACHED_SERVER_NAME}:/home/ubuntu/ --zone europe-west3-a
gcloud compute scp --scp-flag=-r ../part4 ubuntu@${MEMCACHED_SERVER_NAME}:/home/ubuntu/ --zone europe-west3-a

gcloud compute ssh --zone "europe-west3-a" "${MEMCACHED_SERVER_NAME}"  --project "cca-eth-2023-group-49" \
	-- "cd /home/ubuntu
		sudo apt-get update
		sudo apt install -y memcached libmemcached-tools
		# sudo systemctl status memcached
		sudo cat memcached_config.txt > /etc/memcached.conf
		sudo systemctl restart memcached
		sudo apt install python3-pip
		pip3 install psutil
		pip3 install docker
		pip3 install argparse" 

# ---------------------------- Start Test On Client Agent ----------------------------

# gcloud compute ssh --zone "europe-west3-a" "${AGENT_INTERNAL_NAME}"  --project "cca-eth-2023-group-49" \
# 	-- "cd memcache-perf
# 		./mcperf -T 16 -A" &

# sh benchmark.sh

# python3.7 plot.py

# ---------------------------- Delete Cluster ----------------------------

# kops delete cluster part4.k8s.local --yes




