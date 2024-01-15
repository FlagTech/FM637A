from Chat_Module import *

# 建立 uploads 資料夾
make_upload_folder('uploads')
sample_rate(30000)  # 聲音輸出採樣率
config(db=15) # 初始音量設定
args = {'music_name': '閣愛妳一擺'}
reply_text, cmd, error = player(args)
print(reply_text)
print(cmd)
print(error)