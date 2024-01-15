from machine import I2S, Pin
from chat_tools import *

record_switch = Pin(18, Pin.IN, Pin.PULL_UP)

wifi_connect("無線網路名稱", "無線網路密碼")
url = "伺服器網址"

config(n_url=url, rb=2048, ssr=30000, msr=4000)

function_mapping = {
    "music": music_player,
    "RGB": RGB
    }

while True:
    if record_switch.value() == 0:
        record(7, LED=True)
        response = upload_pcm()
        if response == "error": 
            continue
        server_reply = chat(url)
        cmd_dict = server_reply["cmd"]
        cmd = cmd_dict['cmd_name']
        args = cmd_dict['cmd_args']
        print(f'你: {server_reply["user"]}')
        print(f'語音助理: {server_reply["reply"]}')
        print(f'指令：{cmd}')
        gc.collect()
        if cmd in function_mapping:
            function_mapping[cmd](args)
        else :
            audio_player(True,'temp.wav')