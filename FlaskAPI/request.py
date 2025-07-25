# request.py

import requests
from data_input import data_in

URL = 'http://127.0.0.1:5000/predict'
headers = {"Content-Type": "application/json"}
data = {"input": data_in}

response = requests.post(URL, headers=headers, json=data)

print("Status Code:", response.status_code)
print("Response:", response.json())
