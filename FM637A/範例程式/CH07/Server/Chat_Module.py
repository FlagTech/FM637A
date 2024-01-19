'''All mode'''
#架設 server
import os
import wave
import json
import pickle
from dotenv import load_dotenv
from googlesearch import search
load_dotenv(override=True)
from openai import *
from pydub import AudioSegment
# 建立 OpenAI 物件
client = OpenAI()

uploads_dir = None

# ==============初始設定===============
def config(voice='echo',db=20,backtrace=3,system="請使用繁體中文來回答，並盡量簡述回答。", model="gpt-3.5-turbo", max_tokens = 500):
    global n_backtrace, n_system, n_voice, n_model, n_max_tokens
    n_backtrace = backtrace
    n_system = system
    n_voice = voice
    n_model = model
    n_max_tokens = max_tokens
    with open("db.txt", "w") as db_file:
        db_file.write(str(db))
    return

# ==============取得音量存檔===============
def catch_db():
    with open("db.txt", "r") as db_file:
        db = int(db_file.read())
        if db == '': db = 0
    return db

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

# ==============儲存聊天歷史===============
def save_hist(hist):
    try:
        with open('hist.dat', 'wb') as f:
            pickle.dump(hist, f)
    except:
        # 歷史檔開啟錯誤
        print('無法寫入歷史檔')

# ==============儲存對話歷史===============
def save_chat(user, reply):
    n_backtrace = 3
    hist = load_hist(n_backtrace)
    hist_len = n_backtrace * 2
    while len(hist) >= hist_len:
        hist.pop(1)
        hist.pop(0)
    hist += [user, reply]  # 紀錄對話
    save_hist(hist)  # 儲存對話

# ==============加入對話紀錄===============
def chat_history(n_backtrace):
    n_backtrace = int(n_backtrace)
    hist = load_hist(n_backtrace)
    hist_len = n_backtrace * 2
    message = []
    # -------------------------------逐一加上對話紀錄---------------------------
    for i in range(0, hist_len, 2):
        if hist[i] == '':
            continue
        message.append({'role': 'user', 'content': hist[i]})
        message.append({'role': 'assistant', 'content': hist[i + 1]})
    # ------------------------------------------------------------------------
    return message

# ==============載入聊天歷史===============
def load_hist(n_backtrace):
    try:
        with open('hist.dat', 'rb') as f:
            hist = pickle.load(f)
            return hist
    except:
        # 歷史檔不存在
        # print('歷史檔不存在')
        return ['','']*n_backtrace

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

# ==============convert to wav===============
def convert_to_wav(input_file, output_file, format):  # 讀取檔案名稱 輸出檔案名稱
    audio = AudioSegment.from_file(input_file, format=format)  # 將 mp3 轉成 wav
    audio = audio.set_frame_rate(sam_rate)
    audio.export(output_file, format="wav")  # wav 存檔

# ==============pcm to mp3===============
def pcm_to_mp3(input_file, output_file,sam_rate=4000):
    sound = AudioSegment.from_file(input_file, format="pcm", sample_width=2, channels=1, frame_rate=sam_rate)
    sound.export(output_file, format="mp3")

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
def text_to_speech(text):
    file_path = 'uploads/temp.mp3'
    try:
        response = client.audio.speech.create(model="tts-1",
                                              voice=n_voice,
                                              input=text)
    except:
        return
    response.stream_to_file(file_path)
    output_file = 'uploads/temp.wav'  # wav檔案路徑
    convert_to_wav(file_path, output_file, "mp3")  # mp3 to wav
    delete_file(file_path)  # 刪除mp3
    change_sound = add_wav_volume(output_file, -9)
    change_sound.export(output_file, format="wav")  # WAV 存檔
    return output_file

def make_tool_back_msg(tool_msg): # 刪除模型回傳的tool_msg的function_call, 因為傳給模型的格式中無此項
    msg_json = tool_msg.model_dump()
    del msg_json['function_call']
    return msg_json

def make_func_messages(tool_calls):
    messages = []
    for tool_call in tool_calls:
        func = tool_call.function
        args = json.loads(func.arguments)
        print(f'{func.name}({args})')
        fun_reply, cmd, error_info = eval(f'{func.name}({args})')
        messages.append({
            "tool_call_id": tool_call.id, # 叫用函式的識別碼
            "role": "tool", # 以工具角色送出回覆
            "name": func.name, # 叫用的函式名稱
            "content": str(fun_reply) # 傳回值
        })
    return messages,fun_reply, error_info, cmd

def chat_function(user_text, functions=None,messages=None):
    '''
    :param user_text: 使用者訊息
    :param functions: 功能函式
    :param messages: 已建立的訊息串
    :return: reply_text, error_info_all, cmd
    '''
    # 初始變數
    # reply_text:語言模型的回覆 error_info_all:錯誤訊息 cmd:指令資訊
    reply_text, error_info_all, cmd = '', '', {'cmd_name': '', 'cmd_args': {}}
    message = chat_history(n_backtrace)  # 加入對話紀錄 參數為記錄對話的組數
    if messages == None:
        # 無已建立的訊息, 則直接使用 user_text 加入對話紀錄
        message.append({'role': 'system', 'content': n_system})
        message.append({"role": "user", "content": f"{user_text}"})
    else:
        message+=messages # 加入已建立的訊息
    tools = {}
    tool_auto = None
    if functions:
        # 當有函式存在則建立 tools
        tools = {'tools': functions}
        tool_auto = "auto"
    try:
        # 建立 gpt 訊息物件
        response = client.chat.completions.create(
            model=n_model,
            messages=message,
            max_tokens=n_max_tokens,
            **tools,
            tool_choice=tool_auto
        )
    except Exception as e:
        try:
            e_code = e.status_code
        except:
            return '', 'API key 不正確', cmd
        if e_code == 401:
            error_info_all += 'API key 不正確'
        elif e_code == 429:
            error_info_all += 'API 已超出當前配額, 您的積分已用完或已達到每月最高支出'
        elif e_code == 500:
            error_info_all += 'Open AI API 伺服器出現問題'
        elif e_code == 503:
            error_info_all += 'Open AI API 伺服器流量過高, 請稍後再重試'
        else:
            error_info_all += str(e)
        return '', error_info_all, cmd
    # 顯示 tokens
    # prompt_tokens = response.usage.prompt_tokens
    # completions_tokens = response.usage.completion_tokens
    # total_tokens = response.usage.total_tokens
    # print(f'prompt_tokens: {prompt_tokens}\ncompletions_tokens: {completions_tokens}\ntotal_tokens: {total_tokens}')

    res_choices = response.choices[0] # 取得模型回復資訊
    finish_reason = res_choices.finish_reason # 取得回復狀態
    if finish_reason == "stop": # 一般對話
        reply_text = res_choices.message.content # 取得回復訊息

    elif finish_reason == "tool_calls": # 呼叫功能
        tool_calls = response.choices[0].message.tool_calls
        msges, fun_reply, error_info_all, cmd = make_func_messages(tool_calls)  # 呼叫功能的回覆(函式回傳的資料)
        if tool_calls[0].function.name in ['find_best_train','google_search']:
            # 如果呼叫功能為查詢火車或網路查詢，會回傳資料給模型
            messages = [{
                "role": "user",
                "content": f"{user_text}"},
                make_tool_back_msg(response.choices[0].message),  # 傳回 AI 傳給我們的 function calling 結果
            ] + msges
            reply_text, error_info_all, cmd = chat_function('', functions=functions,messages=messages)
        else:# 其他功能直接回傳結果
            reply_text = fun_reply

    elif finish_reason == "length": # 訊息超過限制
        reply_text = res_choices.message.content
        error_info_all += '語句未完成, 受到 tokens 限制'
    return reply_text, error_info_all, cmd

def translate(args):
    """
    Args:
        args: {'target_result': string}
    Returns: reply_text, cmd, error_info
    """
    target_result = args.get("target_result", None)
    cmd = {'cmd_name': '', 'cmd_args': {}}
    error_info = ''
    reply_text = target_result
    return reply_text, cmd, error_info

# ==============套件版 google_search===============
def normal_search(keyword,num):
    search_info = search(keyword, advanced=True, num_results=num)
    content = "以下是最新資訊：\n"
    for item in search_info:
        content += f"標題：{item.title}\n"
        content += f"摘要：{item.description}\n\n"
    return content

# ==============官方 google search api===============
def custom_search(query,num):
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    SEARCH_ENGINE_ID = os.getenv("SEARCH_ENGINE_ID")
    url = f"https://www.googleapis.com/customsearch/v1?key={GOOGLE_API_KEY}&cx={SEARCH_ENGINE_ID}&q={query}&num={num}"
    response = requests.get(url)
    data = response.json()
    content = "以下是最新資訊：\n"
    for item in data['items']:
        content += f"標題：{item['title']}\n"
        content += f"摘要：{item['snippet']}\n\n"
    return content

def search_config(API_KEY=False):# 預設使用搜尋套件
    global use_api
    use_api = API_KEY

# ==============google search 功能===============
def google_search(args):
    error_info = ''
    keyword = args.get("user_text", None)
    cmd = {'cmd_name': '', 'cmd_args': {}}
    try:
        if use_api : # 啟用google search API
            reply_text = custom_search(keyword, 5)
        else:
            reply_text = normal_search(keyword, 5)
    except Exception as e:
        print(e)
        reply_text = '網路查詢失敗'
        error_info = e
    return reply_text, cmd, error_info