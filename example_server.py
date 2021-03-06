__author__ = 'pzucco'


import ReliableUDP
import CustomStruct
import time

MessageStruct = CustomStruct.Structure(
    number= CustomStruct.Int,
    message= CustomStruct.String,
)

@ReliableUDP.listener(MessageStruct)
def echo(data, addr):
    print data
    raw = CustomStruct.serialize(MessageStruct, {'number': data['number'] + 1, 'message': 'pong'})
    ReliableUDP.send_reliable(raw, addr)

ReliableUDP.init(port=1000, retry=100)

while 1:
    ReliableUDP.update()
    time.sleep(0.01)

