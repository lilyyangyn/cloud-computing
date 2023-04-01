#!/bin/bash

repeat=3
OUTPUT_FOLDER="data"

# ---------------------------- Prepare Yaml ----------------------------	

create_yaml() {
	test_name=$1
	threads_num=$2

	target="parsec"
	if [ test_name = "radix" ]; then
		target="splash2x"
	fi

	echo """apiVersion: batch/v1
kind: Job
metadata:
  name: parsec-${test_name}
  labels:
    name: parsec-${test_name}
spec:
  template:
    spec:
      containers:
      - image: anakli/cca:${target}_${test_name}
        name: parsec-${test_name}
        imagePullPolicy: Always
        command: [\"/bin/sh\"]
        args: [\"-c\", \"./run -a run -S ${target} -p ${test_name} -i native -n ${threads_num}\"]
      restartPolicy: Never
      nodeSelector:
        cca-project-nodetype: \"parsec\"
""" > ${test_name}_${threads_num}.yaml
}

# ---------------------------- Start Test ----------------------------	

kubectl delete jobs --all

# for case in "blackscholes" "canneal" "dedup" "ferret" "freqmine" "radix" "vips"; do
for case in "vips"; do
	echo "" > ${OUTPUT_FOLDER}/${case}.txt
	for threads in 1 2 4 8; do
		create_yaml ${case} ${threads}
		echo "------ Threads NUM ${threads} ------" >> data/${case}.txt
		for (( i=1 ; i<=${repeat} ; i++ )); do
			echo "------ Start test on ${case} with ${threads} threads. Repeat ${i} ------"
			kubectl create -f ${case}_${threads}.yaml
			sleep 30
			while true; do
				result=$(kubectl get jobs | grep "parsec-${case}")	# NAME, COMPLETIONS, DURATION, AGE
				completions=$(echo ${result} | awk '{print $2}')
				echo "Check job status... Completions: ${completions}"
				if [ $completions = "1/1" ]; then
					echo ${result} | tee >> ${OUTPUT_FOLDER}/${case}.txt
					break
				fi
				sleep 30
			done
			kubectl delete jobs --all
			echo "------ Finish test on ${case} with ${threads} threads. Repeat ${i} ------"
			sleep 5
		done
		rm ${case}_${threads}.yaml
	done
done