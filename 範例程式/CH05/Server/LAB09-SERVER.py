from Chat_Module import *
from flask import Flask, request

# 建立 uploads 資料夾
make_upload_folder('uploads')
app = Flask(__name__) # 建立 app

# 根目錄-測試用
@app.route("/")
def hello():
    return "Welcome to the audio server!"

# 上傳PCM音檔
@app.route("/upload_audio", methods=["POST"])
def upload_audio():
    audio_data = request.data
    with open("uploads/input.pcm", "wb") as audio_file:
        audio_file.write(audio_data)
    user_text,error_info = speech_to_text()
    print(user_text)
    print('Error_info:',error_info)
    return user_text

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)