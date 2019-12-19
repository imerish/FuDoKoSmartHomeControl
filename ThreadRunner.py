import threading


class ThreadRunner:

    def __init__(self, script_helper, api, connection, api_lock, serial_lock):
        self.script_helper = script_helper
        self.api = api
        self.connection = connection
        self.api_lock = api_lock
        self.serial_lock = serial_lock

    def run_threads(self):
        print("Tutaj")
        rss = self.script_helper.run_saving_scripts(self.api, self.api_lock)
        rse = self.script_helper.run_script_execution(connection=self.connection, serial_lock=self.serial_lock,
                                                      api=self.api, api_lock=self.api_lock)
        rsre = self.script_helper.run_script_running_execution(self.api, self.connection, self.api_lock,
                                                               self.serial_lock)
        rss.start()
        rse.start()
        rsre.start()
        rss.join()
        rse.join()
        rsre.join()

    def run(self):
        thread = threading.Thread(target=self.run_threads, args=())
        return thread
