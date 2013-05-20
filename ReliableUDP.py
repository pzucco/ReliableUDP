__author__ = 'pzucco'

import socket
import CustomStruct as cs

ReliablePacketStruct = cs.Structure(
    code= cs.Byte,
    content= cs.RawData,
)

_channels = {}
_socket = None
_buffer = 4096
_retry = 60

def init(**args):
    global _socket, _retry
    if _socket: _socket.close()
    _socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    if 'port' in args: _socket.bind(('', args['port']))
    _socket.setblocking(0)
    _retry = args.get('retry', 60)

def send(string, addr):
    _socket.sendto(string, addr)

def send_reliable(string, addr):
    if not string: return
    if addr not in _channels:
        _channels[addr] = dict(
            queue=    [],
            timeout=  0,
            code_in=  0,
            code_out= 1,
        )
    _channels[addr]['queue'].append(string)

_listeners = {}

def listener(structure):
    def declare(f):
        _listeners[structure] = f
    return declare

@listener(ReliablePacketStruct)
def _receive_ReliablePacketStruct(msg, addr):
    if addr not in _channels:
        _channels[addr] = dict(
            queue=    [],
            timeout=  0,
            code_in=  0,
            code_out= 1,
        )
    channel = _channels[addr]

    if len(msg['content']): # This is a reliable message

        if msg['code'] == (channel['code_in'] + 1) % 256: # This message is new
            channel['code_in'] = msg['code']
            structure, data = cs.deserialize(msg['content'])
            _listeners[structure](data, addr)

        if msg['code'] == channel['code_in']: # Confirm reception
            _socket.sendto(cs.serialize(ReliablePacketStruct, {
                'code': channel['code_in'],
                'content': '',
                }), addr)

    else: # This is a received confirmation

        if msg['code'] == channel['code_out'] and channel['queue']:
            channel['code_out'] = (channel['code_out'] + 1) % 256
            channel['queue'].pop(0)
            channel['timeout'] = 0

def update():
    while 1:
        try:
            string, addr = _socket.recvfrom(_buffer)
            structure, data = cs.deserialize(string)
            _listeners[structure](data, addr)
        except socket.error: break
    for addr, channel in _channels.items():
        if not channel['queue']: continue
        if not channel['timeout'] % _retry:
            _socket.sendto(cs.serialize(ReliablePacketStruct, {
                'code': channel['code_out'],
                'content': channel['queue'][0],
            }), addr)
        channel['timeout'] += 1

def reset(addr):
    del _channels[addr]

def buffered_connections():
    for addr, channel in _channels.items():
        yield addr, channel['timeout']