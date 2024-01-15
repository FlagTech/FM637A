from machine import I2S, Pin, PWM, Timer
import machine
import requests
import network
import time
import math
import uos
import gc

record_switch = Pin(18, Pin.IN, Pin.PULL_UP)
red_pin = PWM(Pin(17), freq=1000, duty=0)
green_pin = PWM(Pin(16), freq=1000, duty=0)
blue_pin = PWM(Pin(4), freq=1000, duty=0)

def wifi_connect(SSID, PASSWORD):
    station = network.WLAN(network.STA_IF)
    if station.isconnected():
        station.disconnect()
        while station.isconnected():
            pass
    print("WiFi 連線中...")
    station.active(True)
    station.connect(SSID, PASSWORD)
    while not station.isconnected():
        pass
    connected_ssid = station.config('essid')
    set_color(0, 1023, 1023)
    print(f"WiFi: {connected_ssid} 已連線")
    time.sleep(1)
    set_color(0, 0, 0)
    
def config(n_url=None, rb=2048, ssr=30000, msr=4000):
    global url, read_buffer, spk_sample_rate, mic_sample_rate, chunk_size
    url = n_url
    read_buffer = rb
    spk_sample_rate = ssr
    mic_sample_rate = msr
    chunk_size = msr*2
    return
    
def delete_files(file_name):
    if file_name in uos.listdir("/"):
        try:
            uos.remove(f"/{file_name}")
        except Exception as e:
            print(f"刪除失敗: {e}")
    else:
        pass
    
def upload_pcm():
    pcm_file = 'input.pcm'
    url_1 = f'{url}/upload_audio'
    gc.collect()
    with open(f"/{pcm_file}", "rb") as file:
        pcm_data = file.read()
    gc.collect()
    response = requests.post(url_1, data=pcm_data)
    try:
        if response.status_code == 200:
            return response.text
        else:
            print('音檔未上傳')
            return "error"
    finally:
        pcm_data = None
        response.close()
    
def chat(url):
    url_1 = f'{url}/chat'
    response = requests.get(url_1)
    try:
        json_text = response.json()
        return json_text
    except:
        return {"user":"","reply":"伺服器錯誤","cmd":{"cmd_name":"","reply":""}}
    finally:
        response.close()

def audio_player(audio_flag, file_name):
    global url,read_buffer,spk_sample_rate,ranbow_on
    r_light,g_light,b_light = save_color()
    url_2 = f'{url}/download/{file_name}'
    response = requests.get(url_2, stream=True)
    if response.status_code == 200:
        print("((( ♫ )))")
    else:
        print('網路錯誤',response.status_code)
        return
    header_size = 44
    response.raw.read(header_size)
    audio_out = I2S(1, sck=Pin(12), ws=Pin(14), sd=Pin(13), mode=I2S.TX, bits=16, format=I2S.MONO, rate=spk_sample_rate, ibuf=10000)
    if audio_flag: # 講話時開啟藍綠燈
        set_color(0, 1023, 1023)
        pass
    elif audio_flag == None: # 講話不開燈
        pass
    else: # 播放音樂時開啟循環燈
        start_ranbow()
    while True:
        gc.collect()
        if record_switch.value() == 0:
            close_light()
            break
        try:
            gc.collect()
            content_byte = response.raw.read(read_buffer)
            if len(content_byte) == 0:
                break
            audio_out.write(content_byte)
            content_byte = None
        except Exception as ret:
            print("播放異常", ret)
            audio_out.deinit()
            break
    audio_out = None
    response.close()
    if audio_flag != None:
        set_color(0, 0, 0)
        set_color(r_light,g_light,b_light)
    gc.collect()
    time.sleep(1)
    
def set_color(red, green, blue):
    red_pin.duty(int(red))
    green_pin.duty(int(green))
    blue_pin.duty(int(blue))

i = 1
ranbow_on = True
def ranbow():
    global i,ranbow_on
    if not ranbow_on:
        return
    i += 1
    breath_period = 2000
    min_duty = 0
    max_duty = 1023
    red_duty = int((max_duty - min_duty) * (1 + math.sin(2 * math.pi * i / breath_period)) / 2 + min_duty)
    green_duty = int((max_duty - min_duty) * (1 + math.sin(2 * math.pi * (i / breath_period - 1/3))) / 2 + min_duty)
    blue_duty = int((max_duty - min_duty) * (1 + math.sin(2 * math.pi * (i / breath_period - 2/3))) / 2 + min_duty)
    red_pin.duty(red_duty)
    green_pin.duty(green_duty)
    blue_pin.duty(blue_duty)

def start_ranbow():
    global tim0, ranbow_on
    ranbow_on = True
    set_color(1023, 0, 1023)
    i = 1
    tim0 = Timer(0)
    tim0.init(period=3, mode=Timer.PERIODIC, callback=lambda t: ranbow())


def close_light():
    global i,ranbow_on
    i = 0
    ranbow_on = False
    try:
        tim0.deinit()
    except:pass
    set_color(0, 0, 0)
    
def music_player(args):
    audio_player(True,'temp.wav')
    gc.collect()
    audio_player(False,'music.wav')
    close_light()
    
def save_color():
    r_light = red_pin.duty()
    g_light = green_pin.duty()
    b_light = blue_pin.duty()
    return r_light,g_light,b_light

def record(sec,LED=True):
    r_light,g_light,b_light = save_color()
    close_light()
    audio_in = I2S(0,sck=Pin(25),ws=Pin(27),sd=Pin(26),
               mode=I2S.RX,bits=16,format=I2S.MONO,
               rate=mic_sample_rate,ibuf=chunk_size)
    recording_time = 0
    ibuf = bytearray(chunk_size)
    pcm = open('/input.pcm', 'wb')
    if LED :
        set_color(1023, 1023, 1023)
    print('---請說話---')
    print('\r🎤:', recording_time, 's', end='')
    while record_switch.value() == 0 and recording_time <sec:
        t_start = time.time()
        audio_in.readinto(ibuf, chunk_size)
        pcm.write(ibuf)
        t_close = time.time()
        recording_time += (t_close-t_start)
        print('\r🎤:', recording_time, 's', end='')
    print('\n---說完了---')
    set_color(r_light,g_light,b_light)
    audio_in = ibuf = None
    pcm.close()
    gc.collect()

def RGB(args):
    red, green, blue = args['red'], args['green'], args['blue']
    if red == "-1":
        audio_player(True,'temp.wav')
        ranbow(2000)
    else:
        set_color(red, green, blue)
        audio_player(None,'temp.wav')
    