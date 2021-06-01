import pygame
import odrive
from odrive.enums import *
import time

class Odrive:
    def __init__(self) -> None:
        self.drive = odrive.find_any()
        time.sleep(1)
        self.set_zero()
        self.set_closed_loop()

    def set_zero(self):
        self.drive.axis0.encoder.set_linear_count(0)
        self.drive.axis1.encoder.set_linear_count(0)
        self.drive.axis0.controller.config.input_mode = 1
        self.drive.axis1.controller.config.input_mode = 1
        self.drive.axis0.controller.config.input_filter_bandwidth = 30
        self.drive.axis1.controller.config.input_filter_bandwidth = 30
        self.drive.axis0.motor.config.current_lim = 65
        self.drive.axis1.motor.config.current_lim = 65
        self.drive.axis0.motor.config.current_lim_margin = 30
        self.drive.axis1.motor.config.current_lim_margin = 30

    def set_idle(self):
        self.drive.axis0.requested_state = AXIS_STATE_IDLE
        self.drive.axis1.requested_state = AXIS_STATE_IDLE

    def set_closed_loop(self):
        self.drive.axis0.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL
        self.drive.axis1.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL
        time.sleep(1)

    def goto(self, mot_0, mot_1):
        self.drive.axis0.controller.input_pos = mot_0
        self.drive.axis1.controller.input_pos = mot_1


class Controller:
    def __init__(self) -> None:
        self.drive = Odrive()
        pygame.init()
        pygame.font.init()
        self.font_name = pygame.font.get_default_font()
        self.font = pygame.font.Font(self.font_name, 20)
        self.window = pygame.display.set_mode((500, 500))
        pygame.display.set_caption("RAH Visual Controller V0.1")
        self.run = True
        self.armed = False
        self.prev_x = 0
        self.prev_y = 0
        self.a0 = 0
        self.a1 = 0

        self.x_offset = 0  #TODO: figure out what these are...
        self.x_multiplier = -98  
        self.y_offset = 0  #TODO: figure out what these are...
        self.y_multiplier = 85  
        

    def calculate_angles(self, target_pos_x, target_pos_y) -> float:
        x = (target_pos_x + self.x_offset) * self.x_multiplier
        y = (target_pos_y + self.y_offset) * self.y_multiplier
        pi = 3.142
        pulley_diameter = 10.0  # cm
        distance_per_revolution = pi * pulley_diameter

        target_angle_0 = (y / distance_per_revolution) - (x / distance_per_revolution)
        target_angle_1 = (y / distance_per_revolution) + (x / distance_per_revolution)

        return target_angle_0, target_angle_1

    def start(self):
        while self.run:
            pygame.time.delay(20)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.run = False

            mouse_x, mouse_y = pygame.mouse.get_pos()
            keys = pygame.key.get_pressed()

            if keys[pygame.K_SPACE]:
                self.armed = True
                self.window.fill((64, 0, 0))
                idkwhatthisis_2 = self.font.render(f"Armed: {self.armed}", True, (255, 0, 0))
                self.prev_x = mouse_x
                self.prev_y = mouse_y
            else:
                self.armed = False
                self.window.fill((10, 10, 10))
                pygame.draw.circle(self.window, (255, 0, 0), (self.prev_x, self.prev_y), (20))
                idkwhatthisis_2 = self.font.render(f"Armed: {self.armed}", True, (200, 200, 200))

            pygame.draw.circle(self.window, (255, 0, 0), (mouse_x, mouse_y), (20))
            pygame.draw.rect(self.window, (0, 255, 0), (mouse_x, 0, 1, 800))
            pygame.draw.rect(self.window, (0, 128, 255), (0, mouse_y, 500, 1))
            idkwhatthisis = self.font.render(f"X: {mouse_x} | Y: {mouse_y}", True, (255, 255, 255))
            idkwhatthisis_3 = self.font.render(f"X: {mouse_x/500} | Y: {(mouse_y)/500}", True, (255, 255, 255))
            idkwhatthisis_4 = self.font.render(f"M0: {self.a0:.3f} | M1: {self.a1:.3f}", True, (255, 255, 255))
            self.window.blit(idkwhatthisis, (0, 0))
            self.window.blit(idkwhatthisis_2, (0, 450))
            self.window.blit(idkwhatthisis_3, (150, 0))
            self.window.blit(idkwhatthisis_4, (200, 450))
            pygame.display.update()

            if self.armed:
                self.a0, self.a1 = self.calculate_angles(mouse_x/500, mouse_y/500)
                self.drive.goto(self.a0, self.a1)

        self.drive.set_idle()
        pygame.font.quit()
        pygame.quit()

if __name__ == "__main__":
    c = Controller()
    c.start()
