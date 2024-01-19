from machine import Pin, I2S
from chat_tools import *
import urequests
import time

led_pin = Pin(5, Pin.OUT)
record_switch = Pin(18, Pin.IN, Pin.PULL_UP)

wifi_connect("無線網路名稱", "無線網路密碼")
url = "伺服器網址"

config(n_url=url, msr=4000)

while True:
    if record_switch.value() == 0:
        record(7)
        server_reply = upload_pcm()
        print(f'語音辨識: {server_reply}')
    time.sleep(0.1)