from machine import I2S, Pin
from chat_tools import *

record_switch = Pin(18, Pin.IN, Pin.PULL_UP)

wifi_connect("無線網路名稱", "無線網路密碼")
url = "伺服器網址"

config(n_url=url, rb=2048, ssr=30000, msr=4000)

function_mapping = {
    "開燈": lambda: set_color(1023, 1023, 1023),
    "白色": lambda: set_color(1023, 1023, 1023),
    "紅色": lambda: set_color(1023, 0, 0),
    "綠色": lambda: set_color(0, 1023, 0),
    "藍色": lambda: set_color(0, 0, 1023),
    "黃色": lambda: set_color(1023, 1023, 0),
    "紫色": lambda: set_color(1023, 0, 1023),
    "藍綠色": lambda: set_color(0, 1023, 1023),
    "循環燈": lambda: start_ranbow(),
    "關燈": lambda: close_light(),
}

while True:
    if record_switch.value() == 0:
        record(7, LED=True)
        response = upload_pcm()
        if response == "error": 
            continue
        server_reply = chat(url)
        cmd = server_reply["cmd"]
        print(f'你: {server_reply["user"]}')
        print(f'關鍵字：{cmd}')
        gc.collect()
        
        if cmd in function_mapping:
            function = function_mapping[cmd]
            function()