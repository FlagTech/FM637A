'''All mode'''
#架設 server
import os
import wave
from dotenv import load_dotenv
load_dotenv(override=True)
from openai import *
from pydub import AudioSegment
# 建立 OpenAI 物件
client = OpenAI()

uploads_dir = None

# ==============初始設定===============
def config(n_voice='echo',n_backtrace=3,n_system="請使用繁體中文來回答，並盡量簡述回答。", n_model="gpt-3.5-turbo", n_maxtokens = 500):
    global backtrace, system, voice_set, chat_model, max_tokens
    backtrace = n_backtrace
    system = n_system
    voice_set = n_voice
    chat_model = n_model
    max_tokens = n_maxtokens
    return

# ==============上傳資料的資料夾===============
def make_upload_folder(file):
    global uploads_dir
    uploads_dir = file
    if not os.path.exists(file):
        # 如果 uploads 資料夾不存在，則建立它
        os.makedirs(file)
        print("已建立 uploads 資料夾")
        return uploads_dir
    else:
        return uploads_dir

# ==============取得音量存檔===============
def catch_db():
    with open("db.txt", "r") as db_file:
        db = int(db_file.read())
        if db == '': db = 0
    return db

# ==============設定採樣率===============
def sample_rate(rate):
    global sam_rate
    sam_rate = rate
    return


# ==============刪除檔案===============
def delete_file(file_path):
    try:
        os.remove(file_path)
    except Exception as e:
        pass

# ==============convert to wav===============
def convert_to_wav(input_file, output_file, format):  # 讀取檔案名稱 輸出檔案名稱
    audio = AudioSegment.from_file(input_file, format=format)  # 將 mp3 轉成 wav
    audio = audio.set_frame_rate(sam_rate)
    audio.export(output_file, format="wav")  # wav 存檔

# ==============pcm to mp3===============
def pcm_to_mp3(input_file, output_file,sam_rate=4000):
    sound = AudioSegment.from_file(input_file, format="pcm", sample_width=2, channels=1, frame_rate=sam_rate)
    sound.export(output_file, format="mp3")

# ==============wav檔音量增大或縮小===============
def add_wav_volume(filename,music_db=0):
    db = catch_db()+music_db
    sound = AudioSegment.from_file(filename, "wav")
    try: # 嘗試調整音量
        # sound.dBFS 會試圖計算音訊數據的均方根（RMS），假如音訊數據的長度不是整數幀就會出錯。
        # print('原始:',sound.dBFS,'額外調整:',db)
        origin_db = sound.dBFS
        delta_db = origin_db + 15  # 一般聲音標準為 -15db
        change_dBFS = db-delta_db
        # print('最後:',change_dBFS)
        return sound.apply_gain(change_dBFS)
    except Exception as e:
        print('音量增大失敗',e)
        return sound


# ==============pcm to wav===============
def pcm2wav(pcm_file, wav_file, channels=1, bits=16, sample_rate=4000):
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


# ==============語音轉文字===============
def speech_to_text():
    input_file = f'{uploads_dir}/input.pcm'
    output_file = f'{uploads_dir}/input.mp3'
    pcm_to_mp3(input_file, output_file)
    delete_file(input_file)  # 刪除 PCM 檔
    with open(output_file, "rb") as audio_file:
        try:
            transcript = client.audio.transcriptions.create(
                model="whisper-1", file=audio_file, response_format="text")
            result = transcript.strip()
            error_info = ''
        except Exception as e:
            result = '無法識別語音'
            error_info = "Audio file is too short."
    return result, error_info


# ==============文字轉語音===============
def text_to_speech(text, voice_set):
    file_path = 'uploads/temp.mp3'
    response = client.audio.speech.create(model="tts-1",
                                          voice=voice_set,
                                          input=text)
    response.stream_to_file(file_path)
    output_file = 'uploads/temp.wav'  # wav檔案路徑
    convert_to_wav(file_path, output_file, "mp3")  # mp3 to wav
    delete_file(file_path)  # 刪除mp3
    change_sound = add_wav_volume(output_file,-9)
    change_sound.export(output_file, format="wav")  # WAV 存檔
    return output_file