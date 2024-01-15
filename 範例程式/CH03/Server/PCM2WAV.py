import wave
from pydub import AudioSegment
# ==============pcm to wav===============
def pcm2wav(pcm_file, wav_file, channels=1, bits=16, sample_rate=8000):
    pcmf = open(pcm_file, 'rb')
    pcmdata = pcmf.read()
    pcmf.close()

    if bits % 8 != 0:
        raise ValueError("bits % 8 must == 0. now bits:" + str(bits))
    # 計算整數偵大小
    integer_frame_size = channels * (bits // 8)
    extra_bytes = len(pcmdata) % integer_frame_size
    if extra_bytes != 0:
        # 如果不是整數偵大小的倍數，則填充零偵至整數偵
        pcmdata += b'\x00' * (integer_frame_size - extra_bytes)

    wavfile = wave.open(wav_file, 'wb')
    wavfile.setnchannels(channels)
    wavfile.setsampwidth(bits // 8)
    wavfile.setframerate(sample_rate)
    wavfile.writeframes(pcmdata)
    wavfile.close()

# ==============wav檔音量增大===============
def add_wav_volume(filename, db):
    sound = AudioSegment.from_file(filename, "wav")
    try: # 嘗試增大音量
        # sound.dBFS 會試圖計算音訊數據的均方根（RMS），假如音訊數據的長度不是整數幀就會出錯。
        change_db = sound.dBFS+db
        change_dBFS = change_db - sound.dBFS
        return sound.apply_gain(change_dBFS)
    except Exception as e:
        print('音量增大失敗',e)
        return sound