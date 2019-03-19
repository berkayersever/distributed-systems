# REST API Implementation in Python

**Group Members:**	Berkay Ersever 19626, Fatih Taşyaran 19321

### Installing
Create Virtual Environment with Python 3.6.6
```
pip install virtualenv
```
```
cd flight-rest-api
```
```
virtualenv venv
```
```
.\venv\Scripts\activate
```
```
pip install -r requirements.txt
```
```
python app.py
```


### Authentication
```
http://127.0.0.1:5000/auth
```
```json
{
  "username": "admin",
  "password": "8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918"
}
```
```python
import http.client

conn = http.client.HTTPConnection("127,0,0,1")

payload = "{\n\t\"to_where\": \"SAW\",\n\t\"from_where\": \"TXL\",\n\t\"date\": \"17-06-2019\"\n}"

headers = {
    'Content-Type': "application/json",
    'Authorization': "JWT eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE1NTI4NTQ2MTQsImlhdCI6MTU1Mjg1NDMxNCwibmJmIjoxNTUyODU0MzE0LCJpZGVudGl0eSI6MX0.Cq5UiLLuc3grQf0ZX2Bvk2x5mSxfm0XDJTmA5CLKRGw", # Put your token here
    'cache-control': "no-cache",
    'Postman-Token': "13a932dd-93bf-4bbf-972e-47125fbd6440"
    }

conn.request("PUT", "flights", payload, headers)

res = conn.getresponse()
data = res.read()

print(data.decode("utf-8"))
```
