import sys
import time
import odrive
from odrive.enums import *
from fibre.protocol import ChannelBrokenException
import logging

logging.basicConfig(level='DEBUG')

odrv = odrive.find_any()

def erase_previous_config(odrv0: object):
    odrv0.erase_configuration()
    logging.warning('Oodrv0 config erased')

def set_pole_pairs(odrv0: object, pole_pairs: int):
    # pole pairs = number of magnets in motor / 2
print(odrv0.axis0.motor.config.pole_pairs)
print(odrv0.axis1.motor.config.pole_pairs)
    logging.warning(f'Both channels set to {pole_pairs} pole pairs')

def unknowns(odrv0):
logging.warning(f"Axis 0 resistance calib max voltage: {odrv0.axis0.motor.config.resistance_calib_max_voltage}")
logging.warning(f"Axis 0 requested current range: {odrv0.axis0.motor.config.requested_current_range}")
logging.warning(f"Axis 0 current control bandwidth: {odrv0.axis0.motor.config.current_control_bandwidth}")
logging.warning(f"Axis 0 torque constant: {odrv0.axis0.motor.config.torque_constant}")
logging.warning(f"Axis 1 resistance calib max voltage: {odrv0.axis1.motor.config.resistance_calib_max_voltage}")
logging.warning(f"Axis 1 requested current range: {odrv0.axis1.motor.config.requested_current_range}")
logging.warning(f"Axis 1 current control bandwidth: {odrv0.axis1.motor.config.current_control_bandwidth}")
logging.warning(f"Axis 1 torque constant: {odrv0.axis1.motor.config.torque_constant}")

def encoder_setup(odrv0: object, cpr: int):
odrv0.axis0.encoder.config.mode = 0  # ENCODER_MODE_HALL This one doesn't work...
odrv0.axis1.encoder.config.mode = 0  # ENCODER_MODE_HALL This one doesn't work...
    logging.warning('Set encoders to INCREMENTAL')
odrv0.axis0.encoder.config.cpr = 4000
odrv0.axis1.encoder.config.cpr = 4000

odrv0.axis0.encoder.config.use_index = True
odrv0.axis1.encoder.config.use_index = True
odrv0.axis0.encoder.config.ignore_illegal_hall_state = True
odrv0.axis1.encoder.config.ignore_illegal_hall_state = True
    logging.warning(f'Set encoders to {cpr} cpr')
logging.warning(f"Axis 0 encoder calib scan distance: {odrv0.axis0.encoder.calib_scan_distance}")
logging.warning(f"Axis 1 encoder calib scan distance: {odrv0.axis1.encoder.calib_scan_distance}")
logging.warning(f"Axis 0 encoder bandwidth: {odrv0.axis0.encoder.bandwidth}")
logging.warning(f"Axis 1 encoder bandwidth: {odrv0.axis1.encoder.bandwidth}")

def controller_setup(odrv0: object, pos_gain: int = 1, vel_limit: int = 0.5):  # Low vel limit (1 turn every 2s to avoid crsahing lol)
    # https://docs.oodrv0robotics.com/control
    odrv0.axis0.controller.config.pos_gain = pos_gain # 20
    odrv0.axis1.controller.config.pos_gain = pos_gain
    logging.warning(f'Set positional gain to {pos_gain}')
    ### NOTE: The VEL gain determines how fast the motor will move from point A to point B, may need to up/ tweak the value
    odrv0.axis0.controller.config.vel_gain = 0.02 * odrv0.axis0.motor.config.torque_constant * odrv0.axis0.encoder.config.cpr
    odrv0.axis1.controller.config.vel_gain = 0.02 * odrv0.axis1.motor.config.torque_constant * odrv0.axis1.encoder.config.cpr
    logging.warning(f'Set velocity gain to 0.02*torque_constant*cpr')
    odrv0.axis0.controller.config.vel_integrator_gain = 0.1 * odrv0.axis0.motor.config.torque_constant * odrv0.axis0.encoder.config.cpr
    odrv0.axis1.controller.config.vel_integrator_gain = 0.1 * odrv0.axis1.motor.config.torque_constant * odrv0.axis1.encoder.config.cpr
    logging.warning(f'Set velocity integrator gain to 0.1*torque_constant*cpr')
odrv0.axis0.controller.config.vel_limit = 10
odrv0.axis1.controller.config.vel_limit = 10
    logging.warning(f'Set velocity limit to {vel_limit}')

def set_position_control_mode(odrv0: object):
odrv0.axis0.controller.config.control_mode = CONTROL_MODE_POSITION_CONTROL
odrv0.axis1.controller.config.control_mode = CONTROL_MODE_POSITION_CONTROL
    logging.warning(f'Set control_mode to CONTROL_MODE_POSITION_CONTROL')

    odrv0.save_configuration()
    logging.warning(f'Saved new config')

    odrv0.reboot()
    logging.warning(f'Rebooting odrv0')
    time.sleep(1)

### NOTE: free motor os any load etc.

def auto_oodrv0_calibration_sequence(odrv0: object):
odrv0.axis0.requested_state = AXIS_STATE_MOTOR_CALIBRATION
odrv0.axis1.requested_state = AXIS_STATE_MOTOR_CALIBRATION
    logging.warning(f'Set state to AXIS_STATE_MOTOR_CALIBRATION, sleeping for 5 s.')
    time.sleep(10)

    if odrv0.axis0.motor.error != 0:
            logging.error(f"Error: Oodrv0 reported an error of {odrv0.axis0.motor.error} while in the state "
            "AXIS_STATE_MOTOR_CALIBRATION. Printing out Oodrv0 motor data for "
            f"debug:\n {odrv0.axis0.motor}")

    if odrv0.axis1.motor.error != 0:
            logging.error(f"Error: Oodrv0 reported an error of {odrv0.axis1.motor.error} while in the state "
            "AXIS_STATE_MOTOR_CALIBRATION. Printing out Oodrv0 motor data for "
            f"debug:\n {odrv0.axis1.motor}")

logging.critical(f"Axis 0 phase inductence is: {odrv0.axis0.motor.config.phase_inductance}, check that it is 0.001 -> 0.0001")
logging.critical(f"Axis 1 phase inductence is: {odrv0.axis1.motor.config.phase_inductance}, check that it is 0.001 -> 0.0001")
logging.critical(f"Axis 0 phase resistance is: {odrv0.axis0.motor.config.phase_resistance}, check that it is 0.1 -> 0.5")
logging.critical(f"Axis 1 phase resistance is: {odrv0.axis1.motor.config.phase_resistance}, check that it is 0.1 -> 0.5")
    a = input('Ok to continue? [y/N]')
    if not (a == 'y' or a == 'Y'):
        logging.info('Exiting...')
        sys.exit(0)

odrv0.axis0.motor.config.pre_calibrated = True
odrv0.axis1.motor.config.pre_calibrated = True
    logging.warning(f'Setting motors to pre calibrated')

    time.sleep(5)
    logging.info("Starting encoder calibration, wait 30s.")
odrv0.axis0.requested_state = AXIS_STATE_ENCODER_OFFSET_CALIBRATION
odrv0.axis1.requested_state = AXIS_STATE_ENCODER_OFFSET_CALIBRATION
    time.sleep(30)

    if odrv0.axis0.encoder.error != 0:
            logging.error(f"Error: Oodrv0 reported an error of {odrv0.axis0.encoder.error} while in the state "
            "AXIS_STATE_MOTOR_CALIBRATION. Printing out Oodrv0 motor data for "
            f"debug:\n {odrv0.axis0.encoder}")

    if odrv0.axis1.encoder.error != 0:
            logging.error(f"Error: Oodrv0 reported an error of {odrv0.axis1.encoder.error} while in the state "
            "AXIS_STATE_MOTOR_CALIBRATION. Printing out Oodrv0 motor data for "
            f"debug:\n {odrv0.axis1.encoder}")

logging.critical(f"Axis 0 encoder offset is: {odrv0.axis0.encoder.config.offset_float}, check that it is 0.5 or 1.5")
logging.critical(f"Axis 1 encoder offset is: {odrv0.axis1.encoder.config.offset_float}, check that it is 0.5 or 1.5")
    a = input('Ok to continue? [y/N]')
    if not (a == 'y' or a == 'Y'):
        logging.info('Exiting...')
        sys.exit(0)

odrv0.axis0.encoder.config.pre_calibrated = True
odrv0.axis1.encoder.config.pre_calibrated = True
    logging.warning(f'Setting encoders to pre calibrated')

    odrv0.save_configuration()
    logging.warning(f'Saved new config')

    odrv0.reboot()
    logging.warning(f'Rebooting odrv0')
    time.sleep(1)

def bootinit_index_search(odrv0):
odrv0.axis0.requested_state = AXIS_STATE_ENCODER_INDEX_SEARCH
odrv0.axis1.requested_state = AXIS_STATE_ENCODER_INDEX_SEARCH

def set_closed_loop_ctrl(odrv0: object):
odrv0.axis0.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL
odrv0.axis1.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL

def set_idle(odrv0: object):
odrv0.axis0.requested_state = AXIS_STATE_IDLE
odrv0.axis1.requested_state = AXIS_STATE_IDLE

def set_current_limit(odrv0: object):
odrv0.axis0.motor.config.current_lim = 15
odrv0.axis1.motor.config.current_lim = 15  # Amps, up this to 90 etc later...

def set_brake_resistance(odrv0):
    pass
    # odrv0.config.brake_resistance = ? // find out brake resistance

def goto_xy(x: float, y: float, odrv0: object):
    pings_per_cm_0 = 10  # NOTE This is completely ARBITRARY!!! and needs to be calibrated
    pings_per_cm_1 = 10  # NOTE This is completely ARBITRARY!!! and needs to be calibrated

    pi = 3.142
    pulley_diameter = 10  # cm
    distance_per_revolution = pi * pulley_diameter


    target_angle_0 = (y / distance_per_revolution) - (x / distance_per_revolution)
    target_angle_1 = (y / distance_per_revolution) + (x / distance_per_revolution)  # TODO: Derive this matrix

    odrv0.axis0.controller.input_pos = target_angle_0  # NOTE TODO DOO NOT RUN THIS BEFORE VERIFYING ENCODER OFFSET STATUS
    odrv0.axis1.controller.input_pos = target_angle_1

odrv0.axis0.controller.input_pos = 10
odrv0.axis1.controller.input_pos = 10

odrv0.axis0.controller.input_pos = 0
odrv0.axis1.controller.input_pos = 0

odrv0.axis0.encoder.set_linear_count(0)
odrv0.axis1.encoder.set_linear_count(0)


# defaults:
# gain_scheduling_width = 10.0 (float)
# enable_vel_limit = True (bool)
# enable_current_mode_vel_limit = True (bool)
# enable_gain_scheduling = False (bool)
# enable_overspeed_error = True (bool)
# control_mode = 3 (int)
# input_mode = 1 (int)
# pos_gain = 50.0 (float)
# vel_gain = 0.1666666716337204 (float)
# vel_integrator_gain = 0.3333333432674408 (float)
# vel_limit = 100.0 (float)
# vel_limit_tolerance = 2.0 (float)
# vel_ramp_rate = 1.0 (float)
# torque_ramp_rate = 0.009999999776482582 (float)
# circular_setpoints = False (bool)
# circular_setpoint_range = 1.0 (float)
# homing_speed = 0.25 (float)
# inertia = 0.0 (float)
# axis_to_mirror = 255 (int)
# mirror_ratio = 1.0 (float)
# load_encoder_axis = 0 (int)
# input_filter_bandwidth = 2.0 (float)
# anticogging:
#   index = 0 (int)
#   pre_calibrated = False (bool)
#   calib_anticogging = False (bool)
#   calib_pos_threshold = 1.0 (float)
#   calib_vel_threshold = 1.0 (float)
#   cogging_ratio = 1.0 (float)
#   anticogging_enabled = True (bool)
