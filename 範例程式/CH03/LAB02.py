from machine import Pin
import time

led_pin = Pin(5, Pin.OUT)
record_switch = Pin(18, Pin.IN, Pin.PULL_UP)

while True:
    print(record_switch.value())
    if record_switch.value() == 0:
        led_pin.value(0)
    else:
        led_pin.value(1)
    time.sleep(0.1)