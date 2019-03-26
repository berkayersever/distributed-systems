import zmq

HOST = '127.0.0.1'
PORT1 = '50007'
PORT2 = '50008'

context = zmq.Context()

p1 = 'tcp://'+ HOST +':'+ PORT1 # how and where to connect
p2 = 'tcp://'+ HOST +':'+ PORT2 # how and where to connect
s = context.socket(zmq.REP) # create reply socket

s.bind(p1) # bind socket to address
s.bind(p2) # bind socket to address

while True:
    message = s.recv() # wait for incoming message
    if not b'STOP' in message: # if not to stop...
        s.send(message + b'*') # append "*" to message
    else: # else...
        s.send(b'Terminating server') # append "*" to message
        break # break out of loop and end
