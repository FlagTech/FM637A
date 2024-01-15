from machine import Pin,I2S
import time

led_pin = Pin(5, Pin.OUT)
record_switch = Pin(18, Pin.IN, Pin.PULL_UP)

mic_sample_rate = 4000
chunk_size = mic_sample_rate * 2

audio_in = I2S(0,
               sck=Pin(25),
               ws=Pin(27),
               sd=Pin(26),
               mode=I2S.RX,
               bits=16,
               format=I2S.MONO,
               rate=mic_sample_rate,
               ibuf=chunk_size
               )

while True:
    if record_switch.value() == 0:
        recording_time = 0
        ibuf = bytearray(chunk_size)
        pcm = open('/input.pcm', 'wb')
        
        led_pin.value(0)
        print('---請說話---')
        print('\r🎤:', recording_time, 's', end='')
        while record_switch.value() == 0 and recording_time <11:
            t_start = time.time()
            audio_in.readinto(ibuf, chunk_size)
            pcm.write(ibuf)
            t_close = time.time()
            recording_time += (t_close-t_start)
            print('\r🎤:', recording_time, 's', end='')
        print('\n---說完了---')
        led_pin.value(1)
        pcm.close()
        break
    time.sleep(0.1)