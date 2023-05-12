import argparse
#import functools
import subprocess
from time import sleep
import time

import psutil
from scheduler import docker_scheduler
#import signal
#import sys

dedup = ("1",
         "dedup_",
         "anakli/cca:parsec_dedup",
         "./bin/parsecmgmt -a run -p dedup -i native -n 1")
fft = ("2,3",
       "radix_",
       "anakli/cca:splash2x_radix",
       "./bin/parsecmgmt -a run -p radix -i native -n 2")
blackscholes = ("2,3",
                "blackscholes_",
                "anakli/cca:parsec_blackscholes",
                "./bin/parsecmgmt -a run -p blackscholes -i native -n 2")
canneal = ("2,3",
           "canneal_",
           "anakli/cca:parsec_canneal",
           "./bin/parsecmgmt -a run -p canneal -i native -n 2")
freqmine = ("2,3",
            "freqmine_",
            "anakli/cca:parsec_freqmine",
            "./bin/parsecmgmt -a run -p freqmine -i native -n 2")
ferret = ("2,3",
          "ferret_",
          "anakli/cca:parsec_ferret",
          "./bin/parsecmgmt -a run -p ferret -i native -n 2")

vips = ("2,3",
          "vips_",
          "anakli/cca:parsec_vips",
          "./bin/parsecmgmt -a run -p vips -i native -n 2")


com3 = '1,2,3'
com2 = "2,3"
def add_memcached_profile():
    name = "memcache"
    pid = -1

    for proc in psutil.process_iter():
        if name in proc.name():
            pid = proc.pid
            break
    #COPIED CODE, TO BE MODIFIED
    cpu_affinity = ",".join(map(str, range(0, 2)))
    # print(f'Setting Memcached CPU affinity to {cpu_affinity}')
    command = "sudo taskset -a -cp {cpu_affinity} {pid}"
    subprocess.run(command.split(" "), stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    #COPIED CODE, TO BE MODIFIED
    return pid, 4


def main():
    q0 = 0
    q1 = 1
    q2 = 2
    config = [dedup, blackscholes, canneal, freqmine, ferret, vips]
    sched = docker_scheduler(q0,q1,q2, config=config)

    psutil.cpu_percent(None, True)


    start = time.time()

    memcache_pid, c = add_memcached_profile()
    proc = psutil.Process(memcache_pid)

    sched.start_job(sched.all_jobs[0], config[1][1])
    x = 1
    y = 0
    while True:
        res = sched.check_isempty()
        if res == True:
            break

        cpu_percentage = proc.cpu_percent()
        # cpu_arr = psutil.cpu_percent(None, True)
        # tot_util_cpu = sum(cpu_arr)

        if cpu_percentage <= 100:
            print(sched.special_job[0])
            if not sched.check_ended(sched.special_job[0], "dedup"):
                if not sched.check_started(sched.special_job[0], "dedup"):
                    sched.start_job(sched.special_job[0], "dedup")
                else:
                    sched.resume_job(sched.special_job[0], "dedup")
            else:
                #if not check_ended()
                sched.modify_cpu_usage(sched.all_jobs[y], com2, config[x][1])

        else:
            if not sched.check_ended(sched.special_job[0], "dedup"):
                sched.pause_job(sched.special_job[0], "dedup")
            else:
                sched.modify_cpu_usage(sched.all_jobs[y], com2, config[x][1])
        #sched.end_job(sched.special_job[0], "dedup")
        sleep(0.25)
        status = sched.end_job(sched.all_jobs[y], config[x][1])
        if status == True:
            x+=1
            if sched.check_isempty():
                break
            sched.start_job(sched.all_jobs[y], config[x][1])
        
        

    end = time.time()


    print("all jobs done in ", end - start, "s")



if __name__ == "__main__":
    main()