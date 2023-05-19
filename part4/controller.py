import argparse
#import functools
import subprocess
from time import sleep
from logger import *
import time

import psutil
from scheduler import docker_scheduler
#import signal
#import sys

dedup = ("1",
         "dedup_",
         "anakli/cca:parsec_dedup",
         "./run -a run -S parsec -p dedup -i native -n 2")
radix = ("2,3",
       "radix_",
       "anakli/cca:splash2x_radix",
       "./run -a run -S splash2x -p radix -i native -n 2")
blackscholes = ("2,3",
                "blackscholes_",
                "anakli/cca:parsec_blackscholes",
                "./run -a run -S parsec -p blackscholes -i native -n 2")
canneal = ("2,3",
           "canneal_",
           "anakli/cca:parsec_canneal",
           "./run -a run -S parsec -p canneal -i native -n 2")
freqmine = ("2,3",
            "freqmine_",
            "anakli/cca:parsec_freqmine",
            "./run -a run -S parsec -p freqmine -i native -n 2")
ferret = ("2,3",
          "ferret_",
          "anakli/cca:parsec_ferret",
          "./run -a run -S parsec -p ferret -i native -n 2")

vips = ("2,3",
        "vips_",
        "anakli/cca:parsec_vips",
        "./run -a run -S parsec -p vips -i native -n 2")


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
    # cpu_affinity = ",".join(map(str, range(0, 2)))
    cpu_affinity = "0,1"
    # print(f'Setting Memcached CPU affinity to {cpu_affinity}')
    command = "sudo taskset -a -cp {cpu_affinity} {pid}"
    subprocess.run(command.split(" "), stdout=subprocess.DEVNULL,
                   stderr=subprocess.STDOUT)
    #COPIED CODE, TO BE MODIFIED
    return pid, 4

COOL_TIME = 0

def main():
    q0 = 0
    q1 = 1
    q2 = 2
    config = [dedup, radix, blackscholes, canneal, freqmine, ferret, vips]
    #config = [dedup, radix]
    sched = docker_scheduler(q0, q1, q2, config=config)

    psutil.cpu_percent(None, True)

    logger = Logger("jobs.txt")

    #logger.log_start()
    start = time.time()

    memcache_pid, c = add_memcached_profile()
    proc = psutil.Process(memcache_pid)
    psc = proc.cpu_percent()
    # if psc >= 100:
    logger.log_start("[0,1] 2")
    # else:
    #     logger.log_start("[0] 2")

    sched.start_job(sched.all_jobs[0], config[1][1])
    logger.log_jobs(SUBJECT[1], Event.START, "[2,3] 2")
    x = 1
    y = 0
    ct = False
    ct_mem = False
    run_de = True
    changed = False
    changed_2 = False
    last_scale_up = time.time()
    while True:
        res = sched.check_isempty()
        if res == True:
            break

        cpu_percentage = proc.cpu_percent()

        # cpu_arr = psutil.cpu_percent(None, True)
        # tot_util_cpu = sum(cpu_arr)

        if not sched.check_ended(sched.special_job[0], "dedup"):
            now = time.time()
            if cpu_percentage < 50:
                if now > last_scale_up + COOL_TIME:
                    if not sched.check_started(sched.special_job[0], "dedup"):
                        sched.start_job(sched.special_job[0], "dedup")
                        logger.log_jobs("dedup", Event.START, "1")
                        run_de = False
                        # logger.log_jobs(SUBJECT[-1], Event.UPDATE, "0")

                        #sleep(0.1)
                        #sched.pause_job(sched.special_job[0], "dedup")
                    else:
                        sched.resume_job(sched.special_job[0], "dedup")
                        if run_de == True:
                            logger.log_jobs("dedup", Event.UNPAUSE)
                            run_de = False
                        # if ct_mem == False:
                        #     logger.log_jobs(SUBJECT[-1], Event.UPDATE, "0")
                        #     ct_mem = True
            else:
                last_scale_up = now
                sched.pause_job(sched.special_job[0], "dedup")
                if run_de == False:
                    logger.log_jobs("dedup", Event.PAUSE)
                    run_de = True
                # if cpu_percentage < 100:
                #     if ct_mem == False:
                #         logger.log_jobs(SUBJECT[-1], Event.UPDATE, "[0]")
                #         ct_mem = True
                # else:
                    # if ct_mem == True:
                    #     logger.log_jobs(SUBJECT[-1], Event.UPDATE, "[0,1]")
                    #     ct_mem = False
        else:
            if ct == False:
                logger.log_jobs("dedup", Event.END)
                ct = True
            now = time.time()
            if cpu_percentage < 70:
                if now > last_scale_up + COOL_TIME:
                    if changed == False:
                        sched.modify_cpu_usage(
                            sched.all_jobs[y], com3, config[x][1])
                        changed = True
                        changed_2 = False
                        logger.log_jobs(SUBJECT[x], Event.UPDATE, "1,2,3")
                    # if ct_mem == False:
                    #     logger.log_jobs(SUBJECT[-1], Event.UPDATE, "0")
                    #     ct_mem = True
            else:
                last_scale_up = now
                if changed_2 == False:
                    #if not check_ended()
                    sched.modify_cpu_usage(
                        sched.all_jobs[y], com2, config[x][1])
                    changed_2 = True
                    changed = False
                    logger.log_jobs(SUBJECT[x], Event.UPDATE, "[2,3]")
                # if cpu_percentage < 100:
                #     if ct_mem == False:
                #         logger.log_jobs(SUBJECT[-1], Event.UPDATE, "[0]")
                #         ct_mem = True
                # else:
                #     if ct_mem == True:
                #         logger.log_jobs(SUBJECT[-1], Event.UPDATE, "[0,1]")
                #         ct_mem = False

 #sched.end_job(sched.special_job[0], "dedup")
        sleep(0.2)
        status = sched.end_job(sched.all_jobs[y], config[x][1])

        if status == True:
            logger.log_jobs(SUBJECT[x], Event.END)
            x += 1
            if sched.check_isempty() and sched.check_ended(sched.special_job[0], "dedup"):
                break
            if not sched.check_isempty():
                sched.start_job(sched.all_jobs[y], str(x))
            if x <= len(config) - 1:
                logger.log_jobs(SUBJECT[x], Event.START, "[2,3] 2")

    end = time.time()

    logger.log_end()
    logger.close()

    print("all jobs done in ", end - start, "s")


if __name__ == "__main__":
    main()
