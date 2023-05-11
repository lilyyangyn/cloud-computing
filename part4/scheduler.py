import docker


class docker_scheduler:
    def __init__(self, q0, q1, q2, config):
        self.client = docker.from_env()
        self.configs = [q0,q1,q2]
        self.all_jobs = []
        self.queue = []
        self.running_jobs = [0]
        #self.client.create_container(config)
        self.load_level = 0
        ct = 0
        for c in config:
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
    
    def change_order_exec(self, config):
        
        return

    def get_cpu_usage(self):

        return
    
    def schedule_next(self):
        return
    
    def get_load_level(self):
        return self.load_level
    
    def start_job(self, container, name):
        print("starting " + name)
        container.start()
        return
    
    def end_job(self, container, name):
        container.reload()
        if container.status == "exited":
            container.remove()
            self.pop_from_queue(name)
            self.all_jobs.pop(0)
            print("job ended")
            return True
        print("job not ended yet")
        return False
    
    def start_running(self):
        
        return
    
    def check_isempty(self):
        if len(self.all_jobs) == 0:
            return True
        else:
            return False