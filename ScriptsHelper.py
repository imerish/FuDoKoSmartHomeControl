import datetime
import time
import threading


class ScriptsHelper:
    saved_scripts = []
    saved_long_term_scripts = []
    saved_scripts_ids = []
    saved_scripts_lock = threading.Lock()

    def run_saving_scripts(self, api, api_lock):
        thread = threading.Thread(target=self.saving_scripts, args=(api, api_lock))
        return thread

    def run_script_execution(self, connection, serial_lock, api, api_lock):
        thread = threading.Thread(target=self.script_execution, args=(connection, serial_lock, api, api_lock))
        return thread

    def run_script_running_execution(self, api, connection, api_lock, serial_lock):
        thread = threading.Thread(target=self.script_running_execution, args=(api, connection, api_lock, serial_lock))
        return thread

    def saving_scripts(self, api, api_lock):
        while 1:
            with self.saved_scripts_lock:
                with api_lock:
                    scripts_ids = api.get_scripts_ids()
                for script_id in scripts_ids:
                    is_script_id_in_ids = str(script_id) in self.saved_scripts_ids
                    if is_script_id_in_ids:
                        print("Script is already saved")
                        pass
                    else:
                        print("Saving script")
                        with api_lock:
                            script_id_helper = api.get_new_script(script_id)
                        self.saved_scripts.append(script_id_helper)
                        self.saved_scripts_ids.append(str(script_id))
                print("_____________________________________________")
            time.sleep(15)

    def script_type_less_than(self, serial_lock, sensor, script, connection, api, api_lock):
        with serial_lock:
            value = connection.get_value_from_sensor(sensor)
        if value < script['conditionValue']:
            self.run_not_end_commands(script['commands'], connection, serial_lock, api, api_lock, script)

    def script_type_equal(self, serial_lock, connection, sensor, script, api, api_lock):
        with serial_lock:
            value = connection.get_value_from_sensor(sensor)
        if value == script['conditionValue']:
            self.run_not_end_commands(script['commands'], connection, serial_lock, api, api_lock, script)

    def script_type_greater_than(self, serial_lock, connection, sensor, script, api, api_lock):
        with serial_lock:
            value = connection.get_value_from_sensor(sensor)
        if value > script['conditionValue']:
            self.run_not_end_commands(script['commands'], connection, serial_lock, api, api_lock, script)

    def script_execution(self, connection, serial_lock, api, api_lock):
        while 1:
            print("script execution")
            time.sleep(0.1)
            with self.saved_scripts_lock:
                for script in self.saved_scripts:
                    time_from_string = str(script['timeFrom'].replace('T', " "))
                    print(time_from_string)
                    time_from = datetime.datetime.strptime(time_from_string, '%Y-%m-%d %H:%M:%S.%f')
                    if time_from <= datetime.datetime.now():
                        if script['sensorId'] is None:
                            self.run_not_end_commands(script['commands'], connection, serial_lock, api, api_lock,
                                                      script)
                            self.make_script_small_again(script)
                        elif script['sensorId']:
                            sensor = script['sensor']
                            if script['conditionType']['type'] == "<":
                                self.script_type_less_than(serial_lock, sensor, script, connection, api, api_lock)
                            elif script['conditionType']['type'] == "=":
                                self.script_type_equal(serial_lock, connection, sensor, script, api, api_lock)
                            elif script['conditionType']['type'] == ">":
                                self.script_type_greater_than(serial_lock, connection, sensor, script, api, api_lock)
                            self.make_script_small_again(script)

    def script_running_execution(self, api, connection, api_lock, serial_lock):
        while 1:
            print("script running execution")
            time.sleep(0.2)
            with self.saved_scripts_lock:
                for script in self.saved_long_term_scripts:
                    if script['timeTo'] is not None:
                        time_to_string = str(script['timeTo'].replace('T', " "))
                        time_to = datetime.datetime.strptime(time_to_string, '%Y-%m-%d %H:%M:%S.%f')
                        if time_to <= datetime.datetime.now():
                            # скрипт окончился, выполняем команды енд и удаляем скрипт
                            self.run_end_commands_and_delete_script(connection, serial_lock, script, api, api_lock)
                            continue
                        if script['sensor'] is None:
                            continue
                        else:
                            if script['conditionType']['type'] == "<":
                                self.reverse_less_condition(script, connection, serial_lock, api, api_lock)
                            elif script['conditionType']['type'] == "=":
                                self.reverse_equal_condition(script, connection, serial_lock, api, api_lock)
                            elif script['conditionType']['type'] == ">":
                                self.reverse_greater_condition(script, connection, serial_lock, api, api_lock)
                    else:
                        # timeTo is none
                        if script['sensor'] is not None:
                            if script['conditionType']['type'] == "<":
                                self.reverse_less_condition(script, connection, serial_lock, api, api_lock)
                            elif script['conditionType']['type'] == "=":
                                self.reverse_equal_condition(script, connection, serial_lock, api, api_lock)
                            elif script['conditionType']['type'] == ">":
                                self.reverse_greater_condition(script, connection, serial_lock, api, api_lock)
                        else:
                            self.delete_script(script, api_lock, api)

    def run_not_end_commands(self, commands, connection, serial_lock, api, api_lock, script):
        for index, command in enumerate(commands):
            if not command['end']:
                self.command_execution(index, command, connection, serial_lock, api, api_lock, script)

    def run_end_commands(self, commands, connection, serial_lock, api, api_lock, script):
        for index, command in enumerate(commands):
            if command['end']:
                self.command_execution(index, command, connection, serial_lock, api, api_lock, script)

    def delete_script(self, script, api_lock, api):
        with api_lock:
            api.delete_script(script['id'])
        self.saved_long_term_scripts.remove(script)
        for i in self.saved_scripts_ids:
            if script['id'] == i:
                self.saved_scripts_ids.remove(i)

    def make_script_great_again(self, script):
        self.saved_scripts.append(script)
        self.saved_long_term_scripts.remove(script)

    def make_script_small_again(self, script):
        self.saved_long_term_scripts.append(script)
        self.saved_scripts.remove(script)

    def run_end_commands_and_delete_script(self, connection, serial_lock, script, api, api_lock):
        self.run_end_commands(script['commands'], connection, serial_lock, api, api_lock, script)
        self.delete_script(script, api_lock, api)

    def reverse_less_condition(self, script, connection, serial_lock, api, api_lock):
        sensor = script['sensor']
        with serial_lock:
            value = connection.get_value_from_sensor(sensor)
        if value > script['conditionValue']:
            self.run_end_commands(script['commands'], connection, serial_lock, api, api_lock, script)
            if script['repeatTimes'] == -1:
                self.make_script_great_again(script)
            else:
                script['repeatTimes'] = script['repeatTimes'] - 1
                if script['repeatTimes'] == 0:
                    self.delete_script(script, api_lock, api)
                else:
                    self.make_script_great_again(script)

    def reverse_equal_condition(self, script, connection, serial_lock, api, api_lock):
        sensor = script['sensor']
        with serial_lock:
            value = connection.get_value_from_sensor(sensor)
        if value != script['conditionValue']:
            self.run_end_commands(script['commands'], connection, serial_lock, api, api_lock, script)
            if script['repeatTimes'] == -1:
                self.make_script_great_again(script)
            else:
                script['repeatTimes'] = script['repeatTimes'] - 1
                if script['repeatTimes'] == 0:
                    self.delete_script(script, api_lock, api)
                else:
                    self.make_script_great_again(script)

    def reverse_greater_condition(self, script, connection, serial_lock, api, api_lock):
        sensor = script['sensor']
        with serial_lock:
            value = connection.get_value_from_sensor(sensor)
        if value < script['conditionValue']:
            self.run_end_commands(script['commands'], connection, serial_lock, api, api_lock, script)
            if script['repeatTimes'] == -1:
                self.make_script_great_again(script)
            else:
                script['repeatTimes'] = script['repeatTimes'] - 1
                if script['repeatTimes'] == 0:
                    self.delete_script(script, api_lock, api)
                else:
                    self.make_script_great_again(script)

    def command_execution(self, index, command, connection, serial_lock, api, api_lock, script):
        x = command['timeSpan'].split(":")
        delay = x[1] * 60 + x[2]
        print("Delay start")
        time.sleep(int(delay))
        print("Delay stop")
        if command['deviceConfiguration']['measure']['measureName'] == "Virtual":
            with api_lock:
                api.notification(script['sensorId'])
        else:
            with serial_lock:
                connection.send_command_to_device(command['deviceConfiguration']['device'],
                                                  command['deviceConfiguration']['value'],
                                                  command['deviceConfiguration']['measure']['id'])
        time.sleep(1)
