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
    reply_text, error_info = '',''
    # =====處理錄音檔並轉成文字=====
    user_text,error = speech_to_text()
    # =====判斷是否成功識別語音=====
    if user_text == "無法識別語音":
        reply_text = user_text
    else:# =====成功識別語音=====
        reply_text, error_info, _ = chat_function(user_text)
        save_chat(user_text, reply_text)
    print(f"USER：{user_text}")
    print(f"Chatgpt：{reply_text}\nerror_info:{error_info}")
    text_to_speech(reply_text)
    reply_dict = {"user":user_text,"reply":reply_text}
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
    config(voice="echo", db=10, backtrace=3,
           system="請使用繁體中文簡答，並只講重點。",
           model="gpt-3.5-turbo",
           max_tokens = 500)
    app.run(host='0.0.0.0', port=5000)