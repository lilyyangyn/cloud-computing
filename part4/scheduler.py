import docker


class docker_scheduler:
    def __init__(self, q0, q1, q2, config):
        self.client = docker.from_env()
        self.configs = [q0, q1, q2]
        self.all_jobs = []
        self.special_job = []
        self.queue = []
        self.running_jobs = [0]
        #self.client.create_container(config)
        self.load_level = 0
        ct = 0
        spec = self.client.containers.create(cpuset_cpus=config[0][0],
                                             name=config[0][1],
                                             detach=True,
                                             auto_remove=False,
                                             image=config[0][2],
                                             command=config[0][3])
        self.special_job.append(spec)

        for c in config[1:]:
            cont = self.client.containers.create(cpuset_cpus=c[0],
                                                 name=c[1],
                                                 detach=True,
                                                 auto_remove=False,
                                                 image=c[2],
                                                 command=c[3])
            self.all_jobs.append(cont)
            self.push_to_queue(ct)
            ct += 1

    def push_to_queue(self, config):
        self.queue.append(config)

        return

    def pop_from_queue(self, config):
        self.queue.remove(config)
        return

    def get_cpu_usage(self):

        return

    def schedule_next(self):
        return

    def get_load_level(self):
        return self.load_level

    def start_job(self, container, name):
        print("starting " + name)
        if container == None or len(self.all_jobs) == 0:
            print("No jobs to start")
            return
        container.start()
        return

    def check_ended(self, container, name):
        if container == None:
            return True
        container.reload()
        if container.status == "exited":
            
            return True
        else:
            return False

    def check_started(self, container, name):
        if container == None:
            return
        container.reload()
        if container.status in ["running", "paused"]:
            return True
        else:
            return False


    def resume_job(self, container, name):
        #print("resuming ", name)
        if container == None:
            return
        container.reload()
        if container.status == "paused":
            print("resuming ", name)
            container.unpause()

    def end_job(self, container, name):
        if container == None:
            return True
        container.reload()
        if container.status == "exited":

            container.remove()
            #self.pop_from_queue(name)
            self.all_jobs.pop(0)
            print("job ended for ", name)
            return True
        # print("job not ended yet for", name)
        return False

    def modify_cpu_usage(self, container, numcpu, name):

        # print("status is", container.status, " for ", name)
        container.reload()

        if container.status != "running" or container == None:
            return
        # print(numcpu)
        # print(container.status)
        print("updating ", name, " to use core ", numcpu)
        container.update(cpuset_cpus=numcpu)

    def pause_job(self, container, name):
        container.reload()
        if container.status in ["running", "restarting"]:
            container.pause()
            print("paused" + name)

    def check_isempty(self):
        if len(self.all_jobs) == 0:
            return True
        else:
            return False
