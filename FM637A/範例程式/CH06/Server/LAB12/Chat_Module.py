'''All mode'''
#架設 server
import os
import wave
import json
import pickle
from dotenv import load_dotenv
load_dotenv(override=True)
from openai import *

# 建立 OpenAI 物件
client = OpenAI()

uploads_dir = None

# ==============初始設定===============
def config(voice='echo',backtrace=3,system="請使用繁體中文來回答，並盡量簡述回答。", model="gpt-3.5-turbo", max_tokens = 500):
    global n_backtrace, n_system, n_voice, n_model, n_max_tokens
    n_backtrace = backtrace
    n_system = system
    n_voice = voice
    n_model = model
    n_max_tokens = max_tokens
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



def chat_function(user_text, functions=None):
    # 使用者的文字,記錄幾組對話紀錄, 限制回傳的tokens數量, 系統訊息, 函式呼叫
    reply_text, error_info_all, cmd = '', '', {'cmd_name': '', 'cmd_args': {}}
    functions_dict = {}
    message = chat_history(n_backtrace)  # 加入對話紀錄 參數為記錄對話的組數
    message.append({'role': 'system', 'content': n_system})
    message.append({"role": "user", "content": f"{user_text}"})
    if functions:
        functions_dict = {'functions':functions}
    try:
        response = client.chat.completions.create(
            model=n_model,
            messages=message,
            max_tokens=n_max_tokens,
            **functions_dict
        )
    except Exception as e:
        e_code = e.status_code
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
        return '', error_info_all

    prompt_tokens = response.usage.prompt_tokens
    completions_tokens = response.usage.completion_tokens
    total_tokens = response.usage.total_tokens
    print(f'prompt_tokens: {prompt_tokens}\ncompletions_tokens: {completions_tokens}\ntotal_tokens: {total_tokens}')
    res_choices = response.choices[0]
    finish_reason = res_choices.finish_reason
    if finish_reason == "stop": # 一般對話
        reply = res_choices.message.content
        reply_text = reply

    elif finish_reason == "length":
        reply = res_choices.message.content
        reply_text = reply
        error_info_all += '語句未完成, 受到 tokens 限制'
    return reply_text, error_info_all, cmd