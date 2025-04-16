import requests, json
from decouple import config

token = config('token')

url = 'http://localhost:5000/v1/tasks'

headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
}
data = {
    'config' : {
        'test' : '1234',
    }
}

response = requests.post(url, headers=headers, json=data)
print(response.json())
