from Chat_Module import *
from flask import Flask, request, jsonify

app = Flask(__name__)
uploads_dir = make_upload_folder('uploads')

# 根目錄
@app.route("/")
def hello():
    return "Welcome to the audio server!"

# 上傳PCM音檔 input.pcm
@app.route("/upload_audio", methods=["POST"])
def upload_audio():
    audio_data = request.data
    with open(f'{uploads_dir}/input.pcm', "wb") as audio_file:
        audio_file.write(audio_data)
    return "上傳成功"

@app.route("/chat", methods=["GET"])
def chat():
    cmd = ''
    user_text,error = speech_to_text() # 語音檔轉文字
    light_list = ['開燈','白色','紅色','綠色','藍色','黃色','紫色',
                  '藍綠色','循環燈','關燈']
    max_light_list = sorted(light_list, key=len, reverse=True)
    match_cmd = [keyword for keyword in max_light_list 
                        if keyword in user_text]
    if match_cmd:
        cmd = match_cmd[0]
    reply_dict = {"user":user_text,"cmd":cmd}
    print(reply_dict)
    return jsonify(reply_dict)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)