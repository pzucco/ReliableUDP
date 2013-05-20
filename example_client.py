__author__ = 'pzucco'

import ReliableUDP
import CustomStruct
import random
import time

MessageStruct = CustomStruct.Structure(
    number= CustomStruct.Int,
    message= CustomStruct.String,
)

@ReliableUDP.listener(MessageStruct)
def echo(data, addr):
    print data
    raw = CustomStruct.serialize(MessageStruct, {'number': data['number'] + 1, 'message': 'ping'})
    ReliableUDP.send_reliable(raw, addr)

ReliableUDP.init(retry=100)

raw = CustomStruct.serialize(MessageStruct, {'number': 0, 'message': 'ping'})
ReliableUDP.send_reliable(raw, ('127.0.0.1', 1000))

while 1:
    ReliableUDP.update()
    time.sleep(0.01)