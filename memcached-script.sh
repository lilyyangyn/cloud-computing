#!/bin/bash

repeat=5
INTERNAL_AGENT_IP=10.0.16.7


# no-interference

MEMCACHED_IP=$(kubectl get pod some-memcached --template '{{.status.podIP}}')

gcloud compute ssh --zone "europe-west3-a" "client-measure-tld0"  --project "cca-eth-2023-group-49" \
	-- "cd memcache-perf 
		repeat=${repeat}
		for (( i=1 ; i<=${repeat} ; i++ )); 
		do 
			echo "----- Start ROUDN $i -----" 
			./mcperf -s ${MEMCACHED_IP} --loadonly
			./mcperf -s ${MEMCACHED_IP} -a ${INTERNAL_AGENT_IP}  \
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

	gcloud compute ssh --zone "europe-west3-a" "client-measure-tld0"  --project "cca-eth-2023-group-49" \
		-- "cd memcache-perf 
			repeat=${repeat}
			for (( i=1 ; i<=${repeat} ; i++ )); 
			do 
				echo "----- Start ROUDN $i -----" 
				./mcperf -s ${MEMCACHED_IP} --loadonly
				./mcperf -s ${MEMCACHED_IP} -a ${INTERNAL_AGENT_IP}  \
			           --noload -T 16 -C 4 -D 4 -Q 1000 -c 4 -w 2 -t 5 \
			           --scan 30000:110000:5000
			    echo "----- End ROUDN $i -----"
			    sleep 2
			done" \
		| tee output/interference_${case}.txt

	kubectl delete pods ibench-${case}
	break
done



# ---------------------------- SETUP NODE ----------------------------

# sudo apt-get update
# sudo apt-get install libevent-dev libzmq3-dev git make g++ --yes
# sudo cp /etc/apt/sources.list /etc/apt/sources.list~
# sudo sed -Ei 's/^# deb-src /deb-src /' /etc/apt/sources.list
# sudo apt-get update
# sudo apt-get build-dep memcached --yes
# cd && git clone https://github.com/shaygalon/memcache-perf.git
# cd memcache-perf
# git checkout 0afbe9b
# make

# ---------------------------- Start Client Agent ----------------------------

# gcloud compute ssh --zone "europe-west3-a" "client-agent-vnzz"  --project "cca-eth-2023-group-49" \
	# -- 'cd memcache-perf && nohup ./mcperf -T 16 -A &'


