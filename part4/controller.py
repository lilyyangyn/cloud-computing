import argparse
import functools
import subprocess
from time import sleep

import psutil
from scheduler import docker_scheduler
import signal
import sys

dedup = (
         "dedup",
         "anakli/parsec:dedup-native-reduced",
         "./bin/parsecmgmt -a run -p dedup -i native -n 1")
fft = (
       "splash2x-fft",
       "anakli/parsec:splash2x-fft-native-reduced",
       "./bin/parsecmgmt -a run -p splash2x.fft -i native -n 1")
blackscholes = (
                "blackscholes",
                "anakli/parsec:blackscholes-native-reduced",
                "./bin/parsecmgmt -a run -p blackscholes -i native -n 2")
canneal = (
           "canneal",
           "anakli/parsec:canneal-native-reduced",
           "./bin/parsecmgmt -a run -p canneal -i native -n 2")
freqmine = (
            "freqmine",
            "anakli/parsec:freqmine-native-reduced",
            "./bin/parsecmgmt -a run -p freqmine -i native -n 2")
ferret = (
          "ferret",
          "anakli/parsec:ferret-native-reduced",
          "./bin/parsecmgmt -a run -p ferret -i native -n 3")

def main():
    q0 = 0
    q1 = 1
    q2 = 2
    config = 0
    sched = docker_scheduler(q0,q1,q2, config=config)

    sched.start_job(sched.all_jobs[0], "nm")
    while True:
        res = sched.check_isempty()
        if res == True:
            break

        sleep(0.25)

        status = sched.end_job(sched.all_jobs[0], "nm")
        if status == True:
            sched.start_job(sched.all_jobs[0])
        

    
    print("all jobs done")

        



if __name__ == "__main__":
    main()