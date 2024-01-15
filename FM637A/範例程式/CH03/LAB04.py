from machine import I2S, Pin
from chat_tools import *
import time
import gc

led_pin = Pin(5, Pin.OUT)
record_switch = Pin(18, Pin.IN, Pin.PULL_UP)

spk_sample_rate = 8000
mic_sample_rate = 8000
config(ssr=spk_sample_rate, msr=mic_sample_rate)

audio_out = I2S(1,
                sck=Pin(12),
                ws=Pin(14),
                sd=Pin(13),
                mode=I2S.TX,
                bits=16,
                format=I2S.MONO,
                rate=spk_sample_rate,
                ibuf=8000)
while True:
    if record_switch.value() == 0:
        record(11)
        with open("input.pcm", "rb") as f:
            print('\n---播放---')
            while True:
                data = f.read(1024)
                if not data:
                    data = None
                    break
                data = bytearray([int(sample * 5)
                                  for sample in data])
                audio_out.write(data)
        gc.collect()
    time.sleep(0.1)