import os
import json
import time
import requests
from tdx import TDX
from dotenv import load_dotenv

api_base_url1 = 'https://tdx.transportdata.tw/api/basic/v3/Rail/TRA/'  # 台鐵
api_base_url2 = 'https://tdx.transportdata.tw/api/basic/v2/Rail/THSR/'  # 高鐵
headers = {'user-agent':'Mozilla/5.0'}

load_dotenv()

def TDX_config(API_KEY=False):
    global PASS,tdx_client
    TDX_ID = os.getenv('TDX_ID'),
    TDX_SECRET = os.getenv('TDX_SECRET')
    tdx_client = TDX(TDX_ID, TDX_SECRET)  # 讀取 api ID 與 密碼
    PASS = API_KEY

def station_info(trains):
    """
    取得台鐵或高鐵的所有停靠站
    Args:
        trains:1(台鐵) or 0(高鐵)
    Returns:
        stations
    """
    if trains == 1 : #台鐵
        sta_url = f"{api_base_url1}Station?$select=stationName,stationID"
        if PASS == False:
            res = requests.get(sta_url, headers=headers)
            json_data = res.json()
        else:
            json_data = tdx_client.get_json(sta_url)
        json_data = json_data['Stations']
    elif trains == 0 : #高鐵
        sta_url = f"{api_base_url2}Station?$select=stationName,stationID"
        if PASS == False:
            res = requests.get(sta_url, headers=headers)
            json_data = res.json()
        else:
            json_data = tdx_client.get_json(sta_url)
    stations = {}
    for station in json_data:
        station_name = station['StationName']['Zh_tw']
        station_id = station['StationID']
        stations[station_name] = station_id
    return stations

def stations_time(start_station,end_station):
    now = time.localtime()
    date = f"{now.tm_year}-{now.tm_mon:02d}-{now.tm_mday:02d}"
    url =f"{api_base_url1}DailyTrainTimetable/OD/{start_station}/to/{end_station}/{date}"
    if PASS == False:
        res = requests.get(url,headers=headers)
        json_data = res.json()
    else:
        json_data = tdx_client.get_json(url)
    timetables = []
    for timetable in json_data['TrainTimetables']:
        train_no = timetable['TrainInfo']['TrainNo']
        stop_times = timetable['StopTimes']
        departure_Time = stop_times[0]['DepartureTime']
        arrive_Time = stop_times[1]['ArrivalTime']
        timetables.append({
            "車次":train_no,
            "出發":departure_Time,
            "抵達":arrive_Time
             })
    timetables = sorted(
        timetables,
        key=lambda timetable: timetable["出發"]
    )
    return timetables


def high_stations_time(start_station,end_station):
    now = time.localtime()
    date = f"{now.tm_year}-{now.tm_mon:02d}-{now.tm_mday:02d}"
    url = f"{api_base_url2}DailyTimetable/OD/{start_station}/to/{end_station}/{date}"
    if PASS == False:
        res = requests.get(url, headers=headers)
        json_data = res.json()
    else:
        json_data = tdx_client.get_json(url)
    timetables1 = []
    timetables2 = []
    timetables_full = []
    for timetable in json_data:
        train_no = timetable['DailyTrainInfo']['TrainNo']
        stop_times = timetable['OriginStopTime']
        departure_Time = stop_times['DepartureTime']
        stop_times2 = timetable['DestinationStopTime']
        arrive_Time = stop_times2['ArrivalTime']
        timetables1.append(f'{departure_Time}')
        timetables2.append(f'{arrive_Time}')
        timetables_full.append({
            "車次":train_no,
            "出發":departure_Time,
            "抵達":arrive_Time
             })
    timetables1 = sorted(timetables1)
    timetables2 = sorted(timetables2)
    return timetables1,timetables2,timetables_full

def replace_common_chars(name: str):
    return name.replace('台', '臺')


def get_station_id(stations,station_flag,station_name):
    if station_flag == 1:
        station_name = replace_common_chars(station_name)
    else: pass
    res = stations.get(station_name, '0000')
    return res



def find_best_train(args):
    train = args.get("train", None)
    start_station = args.get("start_station", None)
    end_station = args.get("end_station", None)
    train_time = args.get("train_time", None) # 輔助回傳模型判斷用
    reply,error_info = '',''
    cmd = {'cmd_name': '', 'cmd_args': {}}
    try:
        normal_stations = station_info(1)
        high_stations = station_info(0)
    except:
        error_info = '查詢車次錯誤, 已超過查詢上限, 請使用正確的TDX_ID與TDX_SECRET'
        return reply, cmd, error_info
    if train == '高鐵':
        station_flag = 0
        stations = high_stations
        start_id = get_station_id(stations, station_flag, start_station)
        end_id = get_station_id(stations, station_flag, end_station)
        timetables1,timetables2,timetables_full = high_stations_time(start_id, end_id)
        timetables = timetables_full

    elif train == '台鐵':
        station_flag = 1
        stations = normal_stations
        start_id = get_station_id(stations, station_flag, start_station)  # 起點站
        end_id = get_station_id(stations, station_flag, end_station)  # 終點站
        timetables = stations_time(start_id, end_id)
    else:
        timetables = '請再次查詢'
    return timetables, cmd, error_info

if __name__ == '__main__':
    TDX_config(API_KEY=True)
    args = {"train": "台鐵", "start_station": "台北", "end_station": "台中"}
    reply, cmd, error_info = find_best_train(args)
    for i in reply:
        print(i)