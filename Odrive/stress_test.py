import pygame
import odrive
from odrive.enums import *
import time
from pygame_control import Odrive

points = [[1.147, 2.023], [1.397, 3.556], [-0.121, 3.214], [-0.642, 1.584]]

class StressTest:
    def __init__(self) -> None:
        self.drive = Odrive()
        self.drive.drive.axis0.controller.config.vel_limit = 30
        self.drive.drive.axis1.controller.config.vel_limit = 30
        self.drive.set_zero()
        self.drive.set_idle()

    def start(self):
        self.drive.set_closed_loop()
        while True:
            print(f"FET0: {self.drive.drive.axis0.fet_thermistor.temperature}")
            print(f"FET1: {self.drive.drive.axis1.fet_thermistor.temperature}")
            for p in points:
                self.drive.goto(p[0], p[1])
                time.sleep(0.3)

a = StressTest()
a.start()
