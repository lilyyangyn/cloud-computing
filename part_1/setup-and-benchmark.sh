#!/bin/bash

ethzid="yangyue"

# ---------------------------- Script Starts ----------------------------

gsutil mb gs://cca-eth-2023-group-49-${ethzid}/
export KOPS_STATE_STORE=gs://cca-eth-2023-group-49-${ethzid}/
kops delete cluster part1.k8s.local --yes

PROJECT=`gcloud config get-value project`
kops create -f ../setup-config/part1.yaml
kops create secret --name part1.k8s.local sshpublickey admin -i ~/.ssh/cloud-computing.pub
kops update cluster --name part1.k8s.local --yes --admin
sleep 60
kops validate cluster --wait 10m

# ---------------------------- Running memcached and the mcperf load generator ----------------------------

kubectl create -f ../setup-config/memcache-t1-cpuset.yaml
kubectl expose pod some-memcached --name some-memcached-11211  \
                                    --type LoadBalancer --port 11211 \
                                    --protocol TCP
sleep 60
kubectl get service some-memcached-11211

AGENT_INTERNAL_NAME=$(kubectl get nodes -o wide | grep "client-agent-*" | awk '{print $1}')
# AGENT_INTERNAL_IP=$(kubectl get nodes -o wide | grep "client-agent-*" | awk '{print $6}')
MEASURE_INTERNAL_NAME=$(kubectl get nodes -o wide | grep "client-measure-*" | awk '{print $1}')
# MEASURE_INTERNAL_IP=$(kubectl get nodes -o wide | grep "client-measure-*" | awk '{print $6}')

gcloud compute ssh --zone "europe-west3-a" "${AGENT_INTERNAL_NAME}"  --project "cca-eth-2023-group-49" \
	-- "csudo apt-get update
		sudo apt-get install libevent-dev libzmq3-dev git make g++ --yes
		sudo cp /etc/apt/sources.list /etc/apt/sources.list~
		sudo sed -Ei 's/^# deb-src /deb-src /' /etc/apt/sources.list
		sudo apt-get update
		sudo apt-get build-dep memcached --yes
		cd && git clone https://github.com/shaygalon/memcache-perf.git
		cd memcache-perf
		git checkout 0afbe9b
		make" 

gcloud compute ssh --zone "europe-west3-a" "${MEASURE_INTERNAL_NAME}"  --project "cca-eth-2023-group-49" \
	-- "csudo apt-get update
		sudo apt-get install libevent-dev libzmq3-dev git make g++ --yes
		sudo cp /etc/apt/sources.list /etc/apt/sources.list~
		sudo sed -Ei 's/^# deb-src /deb-src /' /etc/apt/sources.list
		sudo apt-get update
		sudo apt-get build-dep memcached --yes
		cd && git clone https://github.com/shaygalon/memcache-perf.git
		cd memcache-perf
		git checkout 0afbe9b
		make" 

# ---------------------------- Start Test On Client Agent ----------------------------

gcloud compute ssh --zone "europe-west3-a" "${AGENT_INTERNAL_NAME}"  --project "cca-eth-2023-group-49" \
	-- "cd memcache-perf
		./mcperf -T 16 -A" &

sh benchmark.sh

python3.7 plot.py

# ---------------------------- Delete Cluster ----------------------------

kops delete cluster part2a.k8s.local --yes




