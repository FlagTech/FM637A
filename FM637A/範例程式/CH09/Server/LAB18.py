from Train_Module import *

TDX_config(API_KEY=True)
args = {"train": "高鐵", "start_station": "台北",
        "end_station": "台中"}
reply, cmd, error_info = find_best_train(args)
for i in reply:
    print(i)