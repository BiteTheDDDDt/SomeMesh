import requests
import json

with open("sample/podInfo-1.json", "r", encoding="utf-8") as podInfoFile:
    podInfo = json.load(podInfoFile)
    payload = {
     'accesslog_path': '/app/accesslog.txt',
     'containers': podInfo,
     'cpu_limit': 4.2,
     'memory_limit': 1280000000.0
    }
    d = json.dumps(payload)
    test_ret = requests.post("http://localhost:8000/optimize", data=d, headers={'Content-Type': 'application/json;charset=UTF-8'})
    print(test_ret.text)