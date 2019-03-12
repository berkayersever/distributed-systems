import requests
import json

# class SearchSimple(Resource)

API_URL = 'http://10.50.54.215:5000'

item_name = 'test-item-2'
# endpoint = '{}/{}'.format(API_URL, item_name)
start = 0
guess = 500000
end = 1000000
value = 500000
endpoint = '{}/todo/{}'.format(API_URL, value)
# print(json.dumps({'result':'success'}))
# content = json.loads(response.json())
# res = (content.get("result"))
# while content not (json.dumps({'result':'success'})):
#     if(json.dumps({'result':'lower'})):
#         value = value / 2
#     elif(json.dumps({'result':'greater'})):
#         value = value * 2
#     print('Value: ', value)
# endpoint = '{}/{}'.format(API_URL, item_name)
# content = json.loads(response.json())
# response = (content.get("result"))

response = requests.get(endpoint)

# response = requests.get(endpoint)
if not response.ok:
    print('item does not exist')

response = requests.put((endpoint), data={'content': 'todo'})
if response.ok:
    print('item created')

response = requests.get(endpoint)
if response.ok:
    content = json.loads(response.json())
    print(content)

print('Value: ', value)
while((content['result'] != 'success')):
    if (content['result'] != 'lower'):
        start = guess - 1
        value = (start + guess) // 2
        print('Value: ', value)
    elif (content['result'] != 'greater'):
        end = guess + 1
        value = (end + guess) // 2
        print('Value: ', value)
    # endpoint = '{}/todo/{}'.format(API_URL, value)
    response = requests.get(endpoint)
    content = json.loads(response.json())