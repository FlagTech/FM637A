from machine import Pin, I2S
from chat_tools import *

record_switch = Pin(18, Pin.IN, Pin.PULL_UP)

wifi_connect("無線網路名稱", "無線網路密碼")
url = "伺服器網址"

config(n_url=url, rb=2048, ssr=20000)

while True:
    if record_switch.value() == 0:
        audio_player(True,'temp.wav')