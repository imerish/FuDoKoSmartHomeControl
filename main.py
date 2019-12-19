import threading
import time
import ArduinoConnect
import FudokoApi
import ScriptsHelper
import threading
import ThreadRunner
import datetime

arduino_connection = ArduinoConnect.ArduinoConnect()
fudoko_api = FudokoApi.FudokoApi()
script_helper = ScriptsHelper.ScriptsHelper()
saved_scripts = []
saved_long_term_scripts = []
saved_scripts_ids = []
saved_scripts_lock = threading.Lock()
saved_long_term_scripts_lock = threading.Lock()
api_lock = threading.Lock()
main_serial_lock = threading.Lock()


def sensors_check():
    while 1:
        with api_lock:
            sensors = fudoko_api.get_all_available_sensors()
        for sensor in sensors:
            with main_serial_lock:
                arduino_connection.get_value_from_sensor(sensor)
            fudoko_api.update_sensor(sensor)
        time.sleep(5)


def run():
    thread = threading.Thread(target=sensors_check)
    return thread


threads = ThreadRunner.ThreadRunner(script_helper, fudoko_api, arduino_connection, api_lock, main_serial_lock)


def main():
    sensors_thread = run()
    sensors_thread.start()
    threads.run()
    threads.run_threads()
    sensors_thread.join()


if __name__ == '__main__':
    main()
