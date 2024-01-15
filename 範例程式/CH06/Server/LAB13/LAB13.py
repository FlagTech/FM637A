from Chat_Module import *

make_upload_folder('uploads')
sample_rate(30000)  # 聲音輸出採樣率
config(voice = "echo", db = 10) # 初始參數設定

while True:
    text = input('輸入文字: ')
    output_file = text_to_speech(text)
    print(f'已轉成語音檔: {output_file}')