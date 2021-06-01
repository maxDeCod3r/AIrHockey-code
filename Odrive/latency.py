import time
from pygame_control import Odrive



drive = Odrive()
print()
print('sending drive in 1 sec')
time.sleep(1)
print('NOW')
drive.goto(0.09, 3.255)
print('5...')
time.sleep(1)
print('4...')
time.sleep(1)
print('3...')
time.sleep(1)
print('2...')
time.sleep(1)
print('1...')
time.sleep(1)
# for i in range(50):
print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
drive.goto(-0.8, 2.29)
time.sleep(1)
drive.set_idle()