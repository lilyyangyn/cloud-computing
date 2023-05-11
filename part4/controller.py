import argparse
#import functools
#import subprocess
from time import sleep
import time

#import psutil
from scheduler import docker_scheduler
#import signal
#import sys

dedup = ("0,1,2,3",
         "dedup_",
         "anakli/cca:parsec_dedup",
         "./bin/parsecmgmt -a run -p dedup_ -i native -n 3")
fft = ("0,1,2,3",
       "radix_",
       "anakli/cca:splash2x_radix",
       "./bin/parsecmgmt -a run -p radix_ -i native -n 3")
blackscholes = ("0,1,2,3",
                "blackscholes_",
                "anakli/cca:parsec_blackscholes",
                "./bin/parsecmgmt -a run -p blackscholes_ -i native -n 3")
canneal = ("0,1,2,3",
           "canneal_",
           "anakli/cca:parsec_canneal",
           "./bin/parsecmgmt -a run -p canneal_ -i native -n 3")
freqmine = ("0,1,2,3",
            "freqmine_",
            "anakli/cca:parsec_freqmine",
            "./bin/parsecmgmt -a run -p freqmine_ -i native -n 3")
ferret = ("0,1,2,3",
          "ferret_",
          "anakli/cca:parsec_ferret",
          "./bin/parsecmgmt -a run -p ferret_ -i native -n 3")

vips = ("0,1,2,3",
          "vips_",
          "anakli/cca:parsec_vips",
          "./bin/parsecmgmt -a run -p vips_ -i native -n 3")

def main():
    q0 = 0
    q1 = 1
    q2 = 2
    config = [dedup, fft, blackscholes, canneal, freqmine, ferret, vips]
    sched = docker_scheduler(q0,q1,q2, config=config)

    start = time.time()

    sched.start_job(sched.all_jobs[0], config[0][1])
    x = 0
    while True:
        res = sched.check_isempty()
        if res == True:
            break

        sleep(0.25)

        status = sched.end_job(sched.all_jobs[0], config[x][1])
        if status == True:
            x+=1
            if sched.check_isempty():
                break
            sched.start_job(sched.all_jobs[0], config[x][1])
        
    end = time.time()
    

    print("all jobs done in ", end - start, "s")

        



if __name__ == "__main__":
    main()