from Chat_Module import *

config(backtrace = 3,
       system = "請使用繁體中文簡答，並只講重點。",
       model="gpt-3.5-turbo",
       max_tokens=500)

while True:
    user_text = input("USER: ")
    if user_text == '':
        break
    reply, error_info, _ = chat_function(user_text)
    print(f'ChatGPT: {reply}')
    if error_info:
        print(f'error: {error_info}')
    save_chat(user_text, reply)