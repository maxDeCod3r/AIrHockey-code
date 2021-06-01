import odrive
import signal
import logging
from odrive.enums import (AXIS_STATE_IDLE,
                          AXIS_STATE_FULL_CALIBRATION_SEQUENCE,
                          AXIS_STATE_CLOSED_LOOP_CONTROL,
                          INPUT_MODE_POS_FILTER)

odrive_params = {
    'current_lim': 50,  # A
    'vel_lim': 60000,  # Rev/s
    'accel_lim': 1000000/1.2,
    'decel_lim': 1000000/1.2,
    'pos_filter': 2,  # For smooth position control
    'encoder_cpr': 4000,  # Counts per revolution
    'desired_velocity': 10000,  # Rev/s
    'brake_resistance': 50  # Ohms
}

logging.basicConfig(level=logging.DEBUG)


class Endstop:
    def __init__(self, pin_ix: int):
        self.endstop_pin = pin_ix
        # Not sure if this is needed???


class Motors:
    def __init__(self, params: dict, odrive_sn: str = None):
        self.params = params
        if odrive_sn:
            try:
                self.drive = odrive.find_any(serial_number=odrive_sn)
            except Exception as err:
                logging.error(f"Encountered error: {err}")
        else:
            self.drive = odrive.find_any()
        self.enable_estop()
        self.set_parameters()
        logging.info(f"Odrive ready, voltage: {self.drive.vbus_voltage}V")

    def digital_estop(self, *_):
        axis0 = self.drive.axis0
        axis1 = self.drive.axis1
        axis0.requested_state = AXIS_STATE_IDLE
        axis1.requested_state = AXIS_STATE_IDLE
        logging.warning('Estop triggered, motors set to Idle')

    def enable_estop(self):
        signal.signal(signal.SIGINT, self.digital_estop)
        logging.info('Ctrl+C Estop enabled')

    def set_parameters(self):
        axis0 = self.drive.axis0
        axis1 = self.drive.axis1
        for axis in [axis0, axis1]:
            axis.motor.config.current_lim = self.params.get('current_lim', 1)
            axis.encoder.config.cpr = self.params.get('encoder_cpr', 4000)
            axis.controller.config.vel_limit = self.params.get('vel_lim', 1)
            axis.trap_traj.config.vel_limit = self.params.get('vel_lim', 1)
            axis.trap_traj.config.accel_limit = self.params.get('accel_lim', 1)
            axis.trap_traj.config.decel_limit = self.params.get('decel_lim', 1)
            # axis.controller.config.input_filter_bandwidth = self.params.get('pos_filter', 2)

    def run_calibration(self):
        self.drive.axis0.requested_state = AXIS_STATE_FULL_CALIBRATION_SEQUENCE
        self.drive.axis1.requested_state = AXIS_STATE_FULL_CALIBRATION_SEQUENCE
        while ((self.drive.axis0.current_state != AXIS_STATE_IDLE)
               or (self.drive.axis1.current_state != AXIS_STATE_IDLE)):
            pass
        self.drive.save_configuration()

    def enable_watchdog(self):
        self.drive.axis0.config.watchdog_timeout = 1  # second
        self.drive.axis1.config.watchdog_timeout = 1  # second
        # Don't forget to push the axis.watchdog_feed() at n second intervals
        self.drive.axis0.config.enable_watchdog = True
        self.drive.axis1.config.enable_watchdog = True

    def set_idle(self):
        self.drive.axis0.requested_state = AXIS_STATE_IDLE
        self.drive.axis1.requested_state = AXIS_STATE_IDLE

    def set_closed_loop(self):
        self.drive.axis0.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL
        self.drive.axis1.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL

    def set_filtered_pos_ctrl(self):
        self.drive.axis0.controller.config.input_mode = INPUT_MODE_POS_FILTER
        self.drive.axis1.controller.config.input_mode = INPUT_MODE_POS_FILTER

    def index_calibration(self):
        pass
        #  TODO: here it will look for the endstop and zero the encoder counts
        #  Freeze one motor
        #  Move other motor slowly until endstop activated
        #  https://docs.odriverobotics.com/api/odrive.endstop.config

    def cartesian_to_angle(self, position: dict):
        '''
        input dict: poisition = {
                'x': 0->100,
                'y': 0->100
            }
        '''
        target_x = position['x']
        target_y = position['y']
        # TODO: this
        print(target_x, target_y)

    def move_to_angle(self, axis: object, position: int):
        '''
        This is for position ctrl, not trajectory!!!
        '''
        axis.controller.move_to_pos(position)
        # PID control: https://docs.odriverobotics.com/control.html


if __name__ == "__main__":
    motors = Motors(odrive_params)
