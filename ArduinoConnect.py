import time
import subprocess
import termios
import serial


class ArduinoConnect:
    ser = serial.Serial('/dev/ttyUSB0', 9600,
                        timeout=0.5,  # IMPORTANT, can be lower or higher
                        )
    command = "ls /dev/tty* | grep /dev/ttyUSB"

    def set_port(self):
        port = str(subprocess.check_output(self.command, shell=True))
        port = port.rstrip()
        if self.ser.is_open:
            self.ser.close()
        else:
            pass
        self.ser.setPort(port)
        self.ser.baudrate = 9600
        self.ser.timeout = 0.5
        self.ser.open()
        time.sleep(5)

    def get_value_from_sensor(self, sensor):
        while 1:
            try:
                if self.ser.is_open:
                    pass
                else:
                    break
                self.ser.flush()
                send_string = "1\n" + str(sensor['pin']) + "\n" + str(sensor['sensorType']['id'])
                self.ser.write(send_string.encode())
                self.ser.flush()
                i = 0
                while self.ser.in_waiting == 0 and i < 4:
                    time.sleep(0.5)
                    i = i + 1

                if self.ser.in_waiting > 0:
                    line = float(self.ser.readline())
                    sensor['value'] = line
                    return line
            except serial.SerialException:
                continue
            except termios.error:
                if self.ser.is_open:
                    self.ser.close()
                continue
            except IOError:
                continue
            except subprocess.CalledProcessError:
                continue

    def send_command_to_device(self, device, value, measure):
        while 1:
            try:
                if self.ser.is_open:
                    print(self.ser.is_open)
                else:
                    break
                self.ser.flush()
                send_string = "2\n" + str(device['pin']) + "\n" + str(value) + "\n"+str(measure)
                print(send_string)
                self.ser.write(send_string.encode())
                self.ser.flush()
                i = 0
                while self.ser.in_waiting == 0 and i < 4:
                    time.sleep(0.5)
                    i = i + 1

                if self.ser.in_waiting > 0:
                    line = self.ser.readline()
                    # print(line)
                break
            except serial.SerialException:
                continue
            except termios.error:
                if self.ser.is_open:
                    self.ser.close()
                continue
            except IOError:
                continue
            except subprocess.CalledProcessError:
                continue
