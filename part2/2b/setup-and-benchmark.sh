#!/bin/bash

ethzid="yangyue"

# ---------------------------- Script Starts ----------------------------

gsutil mb gs://cca-eth-2023-group-49-${ethzid}/
export KOPS_STATE_STORE=gs://cca-eth-2023-group-49-${ethzid}/
kops delete cluster part2b.k8s.local --yes

PROJECT=`gcloud config get-value project`
kops create -f ../setup-config/part2b.yaml
kops create secret --name part2b.k8s.local sshpublickey admin -i ~/.ssh/cloud-computing.pub
kops update cluster --name part2b.k8s.local --yes --admin
sleep 60
kops validate cluster --wait 10m

# ---------------------------- Job Starts ----------------------------

PARSEC_SERVER_INFO=$(kubectl get nodes -o wide | grep "parsec-server-*")
PARSEC_SERVER_NAME=$(echo ${PARSEC_SERVER_INFO} | awk '{print $1}')
PARSEC_SERVER_INTERNAL_IP=$(echo ${PARSEC_SERVER_INFO} | awk '{print $6}')

kubectl label nodes "${PARSEC_SERVER_NAME}" cca-project-nodetype=parsec

sh benchmark.sh

python3.7 plot.py

# # ---------------------------- Delete Cluster ----------------------------

kops delete cluster part2b.k8s.local --yes




