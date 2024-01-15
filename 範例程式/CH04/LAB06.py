from chat_tools import *
import requests

wifi_connect("無線網路名稱", "無線網路密碼")
url = "伺服器網址"

response = requests.get(url)
print(response.text)