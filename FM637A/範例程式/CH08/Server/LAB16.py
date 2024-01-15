from Chat_Module import *

chat_model = "gpt-3.5-turbo"
user_text = "2024有哪些電視劇"
args = {"user_text":user_text}
search_config(API_KEY=False) # False 為使用搜尋套件
reply_text, cmd, error_info = google_search(args)
print(reply_text)