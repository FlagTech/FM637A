from machine import Pin, I2S
from chat_tools import *
import time

led_pin = Pin(5, Pin.OUT)
record_switch = Pin(18, Pin.IN, Pin.PULL_UP)

wifi_connect("無線網路名稱", "無線網路密碼")
url = "伺服器網址"

config(n_url=url, rb=2048, ssr=8000, msr=8000)

while True:
    if record_switch.value() == 0:
        record(3)
        server_text = upload_pcm()
        print(f'server_text: {server_text}')
        audio_player(True,'input.pcm')