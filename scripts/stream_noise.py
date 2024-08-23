import argparse
import numpy as np
import time
import zmq

from epoc import ConfigurationClient, auth_token, redis_host

c = ConfigurationClient(redis_host(), token=auth_token())
nrows = c.nrows
ncols = c.ncols

port = 4545
context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.bind(f'tcp://*:{port}')


frame_nr = 0
while True:
    data = np.random.rand(nrows, ncols).astype(np.float32)
    socket.send_multipart([np.array(frame_nr).tobytes(), data.tobytes()])
    frame_nr += 1
    time.sleep(0.2)
    print(frame_nr)