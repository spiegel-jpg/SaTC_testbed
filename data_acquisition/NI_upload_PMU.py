import socket
import json
import datetime, time
from typing import Sized
import pytz
import json
import requests
import threading
from influxdb import InfluxDBClient
import warnings
import pandas as pd
from waveform_to_PMU import feature_extract
import numpy as np

warnings.filterwarnings("ignore")


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("localhost", 8089))
server.listen(1)


time_format = "%Y-%m-%d %H:%M:%S"
tz_NY = pytz.timezone("America/New_York")


# influxDB config
host = "sensorweb.us"
username = "test"
port = 8086
pwd = "sensorweb"
dbName = "testdb"
measurement = "NI_Waveform"
location = "sensorweb128"
isSSL = True
client = InfluxDBClient(
    host=host, port=port, username=username, password=pwd, database=dbName, ssl=isSSL
)


def df_int_to_float(df):
    for i in range(len(df)):
        for j in range(len(df[i])):
            df[i][j] = float(df[i][j])
    return df


while True:
    conn, addr = server.accept()
    cmnd = conn.recv(6*2000*4*8)  # 6 channels * 2khz * 4bytes * 8bit
    data_array = json.loads(cmnd.decode())

    # value_list is uploaded to influxdb
    value_list = data_array
    value_list = df_int_to_float(value_list)
    value_list = np.array(value_list)

    features = feature_extract(value_list, f_s=5000)
    # ts = datetime.datetime.strptime(start_time, time_format)
    # ts = tz_NY.localize(ts)
    currentTime = datetime.datetime.now(tz_NY)
    timestamp = int(currentTime.timestamp() * 1000000000)
    writeData = [
        {
            "measurement": measurement,
            "tags": {"location": [location]},
            "fields": {
                "sensor1_DC_mag": value_list[0][0],
                "sensor1_DC_freq": value_list[1][0],
                "sensor1_DC_angle": value_list[2][0],
                "sensor1_DC_thd": value_list[3][0],
                "sensor1_AC_mag": value_list[4][0],
                "sensor1_AC_freq": value_list[5][0],
                "sensor1_AC_angle": value_list[6][0],
                "sensor1_AC_thd": value_list[7][0],
                "sensor2_DC_mag": value_list[8][0],
                "sensor2_DC_freq": value_list[9][0],
                "sensor2_DC_angle": value_list[10][0],
                "sensor2_DC_thd": value_list[11][0],
                "sensor2_AC_mag": value_list[12][0],
                "sensor2_AC_freq": value_list[13][0],
                "sensor2_AC_angle": value_list[14][0],
                "sensor2_AC_thd": value_list[15][0],
                "sensor3_DC_mag": value_list[16][0],
                "sensor3_DC_freq": value_list[17][0],
                "sensor3_DC_angle": value_list[18][0],
                "sensor3_DC_thd": value_list[19][0],
                "sensor3_AC_mag": value_list[20][0],
                "sensor3_AC_freq": value_list[21][0],
                "sensor3_AC_angle": value_list[22][0],
                "sensor3_AC_thd": value_list[23][0],
            },
            "time": timestamp,
        }
    ]

    client.write_points(
        writeData, time_precision="n", batch_size=10000, protocol="json"
    )

server.close()