__author__ = 'pzucco'

import struct

_code = 0
_byte_struct = struct.Struct('!B')
_int_struct = struct.Struct('!I')
_structure = {}

class Base(object):
    def __init__(self):
        global _code
        self.code = _byte_struct.pack(_code)
        _structure[_code] = self
        _code += 1

class Atom(Base):
    def __init__(self, format_):
        Base.__init__(self)
        self.format = format_
        self.struct = struct.Struct(format_)
    def write(self, data):
        return self.struct.pack(data)
    def read(self, raw, offset):
        return self.struct.unpack_from(raw, offset)[0], offset + self.struct.size

Byte = Atom('B')
Short = Atom('H')
Int = Atom('I')
SigByte = Atom('b')
SigShort = Atom('h')
SigInt = Atom('i')
Float = Atom('f')
Double = Atom('d')

class List(Base):
    def __init__(self, structure):
        Base.__init__(self)
        self.structure = structure
        if structure.__class__ == Atom:
            self.write = self._write_atoms
            self.read = self._read_atoms
    def write(self, data):
        return _byte_struct.pack(len(data)) + ''.join([self.structure.write(data[i]) for i in range(len(data))])
    def read(self, raw, offset):
        count = _byte_struct.unpack_from(raw, offset)[0]
        offset += 1
        data = []
        for i in range(count):
            update, offset = self.structure.read(raw, offset)
            data.append(update)
        return data, offset
    def _write_atoms(self, data):
        return _byte_struct.pack(len(data)) + struct.pack('!%i%s' % (len(data), self.structure.format), *data)
    def _read_atoms(self, raw, offset):
        length = _byte_struct.unpack_from(raw, offset)[0]
        offset += 1
        format = '!%i%s' % (length, self.structure.format)
        return list(struct.unpack_from(format, raw, offset)), offset + length * struct.calcsize(format)

class Tuple(Base):
    def __init__(self, structure, count):
        Base.__init__(self)
        self.count = count
        self.structure = structure
        if structure.__class__ == Atom:
            self.format = struct.Struct('!%i%s' % (self.count, self.structure.format))
            self.write = self._write_atoms
            self.read = self._read_atoms
    def write(self, data):
        return ''.join([self.structure.write(data[i]) for i in range(self.count)])
    def read(self, raw, offset):
        data = []
        for i in range(self.count):
            update, offset = self.structure.read(raw, offset)
            data.append(update)
        return data, offset
    def _write_atoms(self, data):
        return self.format.pack(*data)
    def _read_atoms(self, raw, offset):
        return self.format.unpack_from(raw, offset), offset + self.format.size


def _string_write(data):
    raw = _byte_struct.pack(len(data))
    return raw + struct.pack('!%is' % len(data), data)
def _string_read(raw, offset):
    length = _byte_struct.unpack_from(raw, offset)[0]
    offset += 1
    return struct.unpack_from('!%is' % length, raw, offset)[0], offset + length

String = Base()
String.write = _string_write
String.read = _string_read


def _raw_data_write(data):
    raw = _int_struct.pack(len(data))
    return raw + data
def _raw_data_read(raw, offset):
    length = _int_struct.unpack_from(raw, offset)[0]
    offset += 4
    return raw[offset:offset+length], offset + length

RawData = Base()
RawData.write = _raw_data_write
RawData.read = _raw_data_read


class Structure(Base):
    def __init__(self, **args):
        Base.__init__(self)

        self.struct = '!'
        self.static = []
        self.dynamic = []
        for field, structure in args.items():
            if structure.__class__ == Atom:
                self.static.append(field)
                self.struct += structure.format
            else:
                self.dynamic.append((field, structure))
        self.struct = struct.Struct(self.struct)

    def write(self, data):
        if data.__class__ != dict: data = data.__dict__
        raw = self.struct.pack(*[data[i] for i in self.static])
        return raw + ''.join([structure.write(data[field]) for field, structure in self.dynamic])

    def read(self, raw, offset):
        data = dict(zip(self.static, self.struct.unpack_from(raw, offset)))
        offset += self.struct.size
        for field, dynamic in self.dynamic:
            update, offset = dynamic.read(raw, offset)
            data[field] = update
        return _aux_constructor(self, data), offset


def _default_aux_constructor(structure, data):
    return data

_aux_constructor = _default_aux_constructor

def set_constructor(constructor):
    global _aux_constructor; _aux_constructor = constructor

def deserialize(raw):
    code = _byte_struct.unpack_from(raw)[0]
    data, _ = _structure[code].read(raw, 1)
    return _structure[code], data

def serialize(structure, data):
    return structure.code + structure.write(data)
