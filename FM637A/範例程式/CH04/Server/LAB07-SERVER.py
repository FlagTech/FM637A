from flask import Flask, request, send_file, abort
import os

app = Flask(__name__) # 建立 app

# 根目錄
@app.route("/")
def hello():
    return "Welcome to the audio server!"

# 下載音檔的路徑
@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    if os.path.exists(filename): # 確認有回覆的音檔
        return send_file(filename, as_attachment=True)
    else:
        return abort(404) # 沒有檔案則回覆 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)