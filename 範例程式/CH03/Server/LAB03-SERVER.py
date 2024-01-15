from PCM2WAV import *

pcm_file = 'input.pcm' # 錄製的檔名
wav_file = 'output.wav' # 輸出的檔名
# 轉成wav檔
pcm2wav(pcm_file, wav_file, channels=1, bits=16,
        sample_rate=4000)