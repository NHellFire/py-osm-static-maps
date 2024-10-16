import logging
from multiprocessing import Manager
from shutil import which

from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService

logging.basicConfig(level=logging.INFO)

class WebdriverPool:
    def __init__(self, workers=4, timeout=None, driver=None, driver_args={}, service=None, service_args={}, options=None, options_callback=None, webdriver_args={}):
        self.num_workers = workers
        self.all = []
        self.spare = Manager().Queue()
        self.timeout = timeout

        # Backwards compatibility
        if webdriver_args:
           driver_args = webdriver_args

        # Use headless Firefox as the default
        if not driver:
            driver = webdriver.Firefox

        if not options:
            options = FirefoxOptions

        if not options_callback:
            options_callback = self.options_callback

        # Newer versions of selenium depend on selenium manager to find drivers,
        # So, use shutil.which in case it's not available
        if not service:
            service = FirefoxService
            service_args["executable_path"] = which("geckodriver")

        self._driver = driver
        self._driver_args = driver_args

        self._options = options
        self._options_callback = options_callback
        self._service = service
        self._service_args = service_args


    def acquire(self):
        if self.timeout == 0:
            idx = self.spare.get_nowait()
        else:
            idx = self.spare.get(True, self.timeout)

        return self.all[idx]

    def release(self, webdriver):
        return self.spare.put(webdriver._pool_id)

    def options_callback(self, options):
        options.add_argument("--headless")

    def start(self):
        for i in range(self.num_workers):
            logging.info("Starting worker %d", i)
            wd_args = self._driver_args.copy()
            wd_args["service"] = self._service(**self._service_args)
            wd_args["options"] = self._options()
            self._options_callback(wd_args["options"])

            wd = webdriver.Firefox(**wd_args)
            wd._pool_id = i
            self.all.append(wd)
            self.spare.put(wd._pool_id)

        logging.info("Started %d workers", self.spare.qsize())


    def stop(self):
        for i in range(self.num_workers):
            logging.info("Stopping worker %d", i)
            try:
                self.all[i].quit()
            except Exception as e:
                # TODO: Check which exceptions are returned on dead process so we can ignore the correct ones
                logging.error(format_exc())

        logging.info("Stopped %d workers", self.num_workers)
        self.all = []
        self.spare = Queue()
