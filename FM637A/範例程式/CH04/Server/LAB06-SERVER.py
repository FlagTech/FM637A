from flask import Flask

app = Flask(__name__) # 建立 app

# 根目錄
@app.route("/")
def hello():
    return "Welcome to the audio server!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)