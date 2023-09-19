import logging
from multiprocessing import Queue
from shutil import which

from selenium import webdriver
from selenium.webdriver.common.utils import free_port
from selenium.webdriver.firefox.service import Service

logging.basicConfig(level=logging.INFO)

class WebdriverPool:
    def __init__(self, workers=4, timeout=None, webdriver_args={}):
        self.num_workers = workers
        self.all = []
        self.spare = Queue()
        self.timeout = timeout

        # Newer versions of selenium depend on selenium manager to find drivers,
        # So, use shuti.which in case it's not available
        if not isinstance(webdriver_args.get("service", None), Service):
            webdriver_args["service"] = Service(executable_path=which("geckodriver"))

        # Start workers
        for i in range(workers):
            logging.info(f"Starting worker {i}")
            webdriver_args["service"].port = free_port()
            wd = webdriver.Firefox(**webdriver_args)
            wd._pool_id = i
            self.all.append(wd)
            self.spare.put(wd._pool_id)

        logging.info("Started %d workers", self.spare.qsize())

    def acquire(self):
        if self.timeout == 0:
            idx = self.spare.get_nowait()
        else:
            idx = self.spare.get(True, self.timeout)

        return self.all[idx]

    def release(self, webdriver):
        return self.spare.put(webdriver._pool_id)
