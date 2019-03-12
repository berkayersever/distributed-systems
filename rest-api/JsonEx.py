import json

x = "test"
y = 123
z = [x, y]
t = {'key1': 'val1', 'key2': 'val2'}
print(json.dumps(x))
print(json.dumps(y))
print(json.dumps(z))
print(json.dumps(t))