import os
from Chat_Module import *
from flask import Flask, request, jsonify, send_file, abort

app = Flask(__name__)
uploads_dir = make_upload_folder('uploads')

# 根目錄
@app.route("/")
def hello():
    return "Welcome to the audio server!"

# 上傳PCM音檔
@app.route("/upload_audio", methods=["POST"])
def upload_audio():
    audio_data = request.data
    with open(f'{uploads_dir}/input.pcm', 'wb') as audio_file:
        audio_file.write(audio_data)
    return "上傳成功"

# 處理聊天請求
@app.route("/chat", methods=["GET"])
def chat():
    reply_text, error_info,cmd = '','',{'cmd_name': '', 'cmd_args': {}}
    # =====處理錄音檔並轉成文字=====
    user_text,error = speech_to_text()
    # =====判斷是否成功識別語音=====
    if user_text == "無法識別語音":
        reply_text = user_text
    else:# =====成功識別語音=====
        functions = [
            {"type": "function",
             "function": {
                 "name": "translate",
                 "description": "翻譯使用者要求的句子: 例如 我要去一趟超市"
                                "義大利語->Al mio cane piace molto fare il bagno",
                 "parameters": {
                     "type": "object",
                     "properties": {
                         "target_result": {
                             "type": "string",
                             "description": "翻譯的結果, 如 Al mio cane piace molto fare il bagno"
                         }
                     },
                     "required": ["target_result"]}
             }},
            {"type": "function",
             "function": {
                 "name": "google_search",
                 "description": "網路查詢，可以取得最新即時資訊，根據"
                                "未知問題可使用此 function",
                 "parameters": {
                     "type": "object",
                     "properties": {
                         "user_text": {
                             "type": "string",
                             "description": "要搜尋的關鍵字, 必須是繁體中文"
                         }
                     },
                     "required": ["user_text"]}
             }},
            {"type": "function",
             "function": {
                 "name": "find_best_train",
                 "description": "查詢高鐵或台鐵(火車)等資訊",
                 "parameters": {
                     "type": "object",
                     "properties": {
                         "train": {
                             "type": "string",
                             "description": "搭乘'高鐵'或'台鐵'"
                         },
                         "start_station": {
                             "type": "string",
                             "description": "起始站名稱"
                         },
                         "end_station": {
                             "type": "string",
                             "description": "終點站名稱"
                         },
                         "train_time": {
                             "type": "string",
                             "description": "指定的時間,24小時制"
                             "若無指定時間則不傳入此參數"
                         }
                     },
                     "required": ["train","start_station",
                                  "end_station"]}
             }},
            {"type": "function",
             "function": {
                "name": "player",
                "description": "輸入歌曲名稱就可以播放音樂",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "music_name": {
                            "type": "string",
                            "description": "歌曲名稱或歌手加歌曲名稱"
                        }
                    },
                    "required": ["music_name"]}
             }},
            {"type": "function",
             "function": {
                "name": "led_function",
                "description": "控制LED燈色及開關LED燈，需要color_nam"
                               "e、red、green、blue 四個參數,利用三個"
                               "參數組合成燈色,數值範圍 0~1023, 白色"
                               "(1023,1023,1023), 關燈(0,0,0), 循環"
                               "燈(-1,-1,-1)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "color_name": {
                            "type": "string",
                            "description": "合適的燈色名稱, 如：黃色、莫"
                                           "蘭迪藍、關燈"
                        },
                        "RED": {
                            "type": "string",
                            "description": "紅色數值, 範圍為0~1023"
                        },
                        "GREEN": {
                            "type": "string",
                            "description": "綠色數值, 範圍為0~1023"
                        },
                        "BLUE": {
                            "type": "string",
                            "description": "藍色數值, 範圍為0~1023"
                        }
                    },
                    "required": ["color_name", "RED", "GREEN", "BLUE"]
                }
            }}
        ]

        reply_text, error_info, cmd = chat_function(user_text, functions)
        save_chat(user_text, reply_text)
    print(f"USER：{user_text}")
    print(f"Chatgpt：{reply_text}\nerror_info:{error_info}")
    text_to_speech(reply_text)
    reply_dict = {"user":user_text,"reply":reply_text,"cmd":cmd}
    return jsonify(reply_dict)

# 下載音檔的路徑
@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    file_path = f'{uploads_dir}/{filename}'
    if os.path.exists(file_path): # 確認有回覆的音檔
        return send_file(file_path, as_attachment=True)
    else:
        return abort(404)

if __name__ == '__main__':
    sample_rate(30000)
    TDX_config(API_KEY=False)
    search_config(API_KEY=False)
    config(voice="echo", db=10, backtrace=3,
           system="請使用繁體中文簡答，並只講重點。",
           model="gpt-3.5-turbo",
           max_tokens = 500)
    app.run(host='0.0.0.0', port=5000)