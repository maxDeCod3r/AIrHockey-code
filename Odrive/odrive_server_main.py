import odrive
from odrive.enums import *
import time
import socket
import atexit

class Odrive:
    def __init__(self) -> None:
        self.drive = odrive.find_any()
        time.sleep(1)
        self.init_odrive()
        self.set_zero()
        self.set_closed_loop()

    def init_odrive(self) -> None:
        self.drive.axis0.controller.config.input_mode = 1
        self.drive.axis1.controller.config.input_mode = 1
        self.drive.axis0.motor.config.current_lim = 70
        self.drive.axis1.motor.config.current_lim = 70
        self.drive.axis0.motor.config.current_lim_margin = 30
        self.drive.axis1.motor.config.current_lim_margin = 30
        self.drive.axis0.controller.config.vel_limit = 10
        self.drive.axis1.controller.config.vel_limit = 10


    def set_zero(self) -> None:
        self.drive.axis0.encoder.set_linear_count(0)
        self.drive.axis1.encoder.set_linear_count(0)

    def set_idle(self) -> None:
        self.drive.axis0.requested_state = AXIS_STATE_IDLE
        self.drive.axis1.requested_state = AXIS_STATE_IDLE

    def set_closed_loop(self) -> None:
        self.drive.axis0.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL
        self.drive.axis1.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL
        time.sleep(1)

    def goto_raw(self, mot_0, mot_1) -> None:
        self.drive.axis0.controller.input_pos = mot_0
        self.drive.axis1.controller.input_pos = mot_1


class Server:
    def __init__(self) -> None:
        self.armed = False
        self.armed = True
        self.x_offset = 0
        self.x_multiplier = -98/1.1 # -98/10  # NOTE: Remove the /10
        self.y_offset = 0
        self.y_multiplier = 85/1.1 # 85/10  # NOTE: Remove the /10
        self.sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        self.udp_host = socket.gethostname()
        self.udp_port = 59200
        self.sock.bind((self.udp_host, self.udp_port))
        self.init_odrive()
        atexit.register(self.at_exit)
        self.control_loop()

    def init_odrive(self) -> None:
        self.drive = Odrive()

    def control_loop(self) -> None:
        while True:
            try:
                data_encoded, _ = self.sock.recvfrom(1024)
                data_dirty = data_encoded.decode()
                data_clean = data_dirty.strip('(').strip(')').split(',')
                target = [0, 0]
                target[0] = float(data_clean[0])
                target[1] = float(data_clean[1])
                if target[0] > 1 or target[0] < 0 or target[1] > 1 or target[1] < 0:
                    print(f"{target} outside 0 to 1 range!")
                    exit(2)
                print(f"Received Message: {data_clean}, type: {type(data_clean)}")
                print(f"Parsed Message: {target}, type: {type(target)}")
                angle_0, angle_1 = self.calculate_angles(target[0], target[1])
                print(f"angles: {angle_0}, {angle_1}")
                if self.armed:
                    self.drive.goto_raw(angle_0, angle_1)
            except Exception as e:
                print(f"Exception: {e}")
                self.drive.set_idle()
                exit(1)

    def calculate_angles(self, target_pos_x, target_pos_y) -> float:
        x = (target_pos_x + self.x_offset) * self.x_multiplier
        y = (target_pos_y + self.y_offset) * self.y_multiplier
        pi = 3.142
        pulley_diameter = 10.0  # cm
        distance_per_revolution = pi * pulley_diameter

        target_angle_0 = (y / distance_per_revolution) - (x / distance_per_revolution)
        target_angle_1 = (y / distance_per_revolution) + (x / distance_per_revolution)

        return target_angle_0, target_angle_1

    def at_exit(self):
        self.drive.set_idle()

s = Server()