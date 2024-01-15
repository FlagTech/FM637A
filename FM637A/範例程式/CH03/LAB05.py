from machine import Pin, I2S
import gc

spk_sample_rate = 8000

audio_out = I2S(1, sck=Pin(12), ws=Pin(14),
                sd=Pin(13),
                mode=I2S.TX,
                bits=16,
                format=I2S.MONO,
                rate=spk_sample_rate,
                ibuf=8000)
gc.collect()
wav_file = open('music.wav', 'rb') 
chunk_size = 2048

header_size = 44
wav_file.seek(header_size)

while True:
    wav_data = wav_file.read(chunk_size)
    if not wav_data:
        break
    audio_out.write(wav_data)
wav_file.close()
audio_out.deinit()
gc.collect()