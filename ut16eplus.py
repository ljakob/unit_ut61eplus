import binascii
import logging
import hid
from glibc import ctypes

log = logging.getLogger(__name__)

"""
protocol of UT61+

parts from an USB trace, parts from experimenting myself, parts from https://github.com/gulux/Uni-T-CP2110
and many 'inspirations' form the decompiled bluetooth app

example response in mV AC

ab . => header
cd . => header
10   => number of bytes that follow including 'checksum'
01   => mode
30 0 => range
20   => digit MSB (can be ' ' or '-') ! number can also be ' OL.  '
20   => digit
35 5 => digit
33 3 => digit
2e . => digit
35 5 => digit
34 4 => digit LSB
01   => progress1
00   => progress2 => progress = progress1*10 + progress2 - meaning is not clear yet
30 0 => Bitmask: Max,Min,Hold,Rel
34 4 => Bitmask: !Auto,Battery,HvWarning
30 0 => Bitmask: !DC,PeakMax,PeakMin,BarPol
03   => sum over all - MSB - sum from 0xab to 0x30
8d . => sum over all - LSB




"""


class Measurement:
    _MODE = ['ACV', 'ACmV', 'DCV', 'DCmV', 'Hz', '%', 'OHM', 'CONT', 'DIDOE', 'CAP', '°C', '°F', 'DCuA', 'ACuA', 'DCmA', 'ACmA',
             'DCA', 'ACA', 'HFE', 'Live', 'NCV', 'LozV', 'ACA', 'DCA', 'LPF', 'AC/DC', 'LPF', 'AC+DC', 'LPF', 'AC+DC2', 'INRUSH']
    _UNITS = {'%': {'0': '%'},
              'AC+DC': {'1': 'A'},
              'AC+DC2': {'1': 'A'},
              'AC/DC': {'0': 'V', '1': 'V', '2': 'V', '3': 'V'},
              'ACA': {'1': 'A'},
              'ACV': {'0': 'V', '1': 'V', '2': 'V', '3': 'V'},
              'ACmA': {'0': 'mA', '1': 'mA'},
              'ACmV': {'0': 'mV'},
              'ACuA': {'0': 'uA', '1': 'uA'},
              'CAP': {'0': 'nF',
                      '1': 'nF',
                      '2': 'uF',
                      '3': 'uF',
                      '4': 'uF',
                      '5': 'mF',
                      '6': 'mF',
                      '7': 'mF'},
              'CONT': {'0': 'Ω'},
              'DCA': {'1': 'A'},
              'DCV': {'0': 'V', '1': 'V', '2': 'V', '3': 'V'},
              'DCmA': {'0': 'mA', '1': 'mA'},
              'DCmV': {'0': 'mV'},
              'DCuA': {'0': 'uA', '1': 'uA'},
              'DIDOE': {'0': 'V'},
              'Hz': {'0': 'Hz',
                     '1': 'Hz',
                     '2': 'kHz',
                     '3': 'kHz',
                     '4': 'kHz',
                     '5': 'MHz',
                     '6': 'MHz',
                     '7': 'MHz'},
              'LPF': {'0': 'V', '1': 'V', '2': 'V', '3': 'V'},
              'LozV': {'0': 'V', '1': 'V', '2': 'V', '3': 'V'},
              'OHM': {'0': 'Ω',
                      '1': 'kΩ',
                      '2': 'kΩ',
                      '3': 'kΩ',
                      '4': 'MΩ',
                      '5': 'MΩ',
                      '6': 'MΩ'},
              '°C': {'0': '°C', '1': '°C'},
              '°F': {'0': '°F', '1': '°F'}}

    _OVERLOAD = set(['.OL', 'O.L', 'OL.', 'OL', '-.OL', '-O.L', '-OL.', '-OL'])

    def __init__(self, b: bytes):
        self.b = b
        self.mode = self._MODE[b[0]]
        self.range = b[1:2].decode('ASCII')
        self.display = b[2:9].decode('ASCII').strip()
        self.overload = self.display in self._OVERLOAD
        if self.overload:
            self.decimal = None
        else:
            self.decimal = float(self.display)
        self.unit = self._UNITS[ self.mode ].get(self.range)
        self.progres = b[9] * 10 + b[10]
        self.max = b[11] & 8 > 0
        self.min = b[11] & 4 > 0
        self.hold = b[11] & 2 > 0
        self.rel = b[11] & 1 > 0
        self.auto = b[12] & 4 == 0
        self.battery = b[12] & 2 > 0
        self.hvwarning = b[12] & 1 > 0
        self.dc = b[13] & 8 > 0
        self.peak_max = b[13] & 4 > 0
        self.peak_min = b[13] & 2 > 0
        self.bar_pol = b[13] & 1 > 0  # meaning not clear

    def __str__(self):
        res = '\n'
        res += f'mode={self.mode}\n'
        res += f'range={self.range}\n'
        res += f'display={self.display}\n'
        res += f'overload={self.overload}\n'
        res += f'decimal={self.decimal}\n'
        res += f'unit={self.unit}\n'
        res += f'max={self.max}\n'
        res += f'min={self.min}\n'
        res += f'hold={self.hold}\n'
        res += f'rel={self.rel}\n'
        res += f'auto={self.auto}\n'
        res += f'battery={self.battery}\n'
        res += f'hvwarning={self.hvwarning}\n'
        res += f'dc={self.dc}\n'
        res += f'peak_max={self.peak_max}\n'
        res += f'peak_min={self.peak_min}\n'
        return res

        for b in self.b:
            l = '{:02x} {}\n'.format(b, chr(b))
            res += l
        return res


class UT16EPLUS:

    CP2110_VID = 0x10c4
    CP2110_PID = 0xEA80

    _SEQUENCE_GET_NAME = bytes.fromhex('AB CD 03 5F 01 DA')
    _SEQUENCE_SEND_DATA = bytes.fromhex('AB CD 03 5E 01 D9')
    _SEQUENCE_SEND_CMD = bytes.fromhex('AB CD 03')

    _COMMANDS = {
        'min_max': 65,
        'not_min_max': 66,
        'range': 70, 
        'auto': 71,
        'rel': 72, 
        'select2': 73, # Hz/USB
        'hold': 74,
        'lamp': 75,
        'select1': 76, # orange
        'p_min_max': 77,
        'not_peak': 78,
    }

    def __init__(self):
        self.dev = hid.Device(vid=self.CP2110_VID, pid=self.CP2110_PID)
        #self.dev.nonblocking = 1
        self._send_feature_report([0x41, 0x01])  # enable uart
        self._send_feature_report([0x50, 0x00, 0x00, 0x25, 0x80, 0x00, 0x00, 0x03, 0x00, 0x00])  # 9600 8N1 - from USB trace
        self._send_feature_report([0x43, 0x02])  # purge both fifos

    def _write(self, b: bytes):
        l = len(b)
        buf = ctypes.create_string_buffer(1 + l)
        buf[0] = l
        buf[1:] = b[0:]
        self.dev.write(buf)

    def _send_feature_report(self, report: bytes):
        l = len(report)
        buf = ctypes.create_string_buffer(l)
        buf[0:l] = report[0:l]
        self.dev.send_feature_report(buf)

    def _readResponse(self) -> bytes:
        # pylint: disable=unsupported-assignment-operation,unsubscriptable-object
        state = 0  # 0=init 1=0xAB received 2=0xCD received 3=we have length
        buf: bytes = None
        index: int = None
        sum: int = 0

        while True:
            x = self.dev.read(64)
            b: int
            for b in x[1:]:  # skip first byte - length from HID

                if state < 3 or index + 2 < len(buf):  # sum all bytes except last 2
                    sum += b

                if state == 0 and b == 0xAB:
                    state = 1
                elif state == 1 and b == 0xCD:
                    state = 2
                elif state == 2:
                    buf = bytearray(b)
                    index = 0
                    state = 3
                elif state == 3:
                    buf[index] = b
                    index += 1
                    if index == len(buf):
                        recevied_sum = (buf[-2] << 8) + buf[-1]
                        log.debug('calculated sum=%04x expected sum=%04x', sum, recevied_sum)
                        if sum != recevied_sum:
                            log.warning('checksum mismatch')
                            return None
                        return buf[:-2]  # drop last 2 bytes at end with checksum
                else:
                    log.warning('unexpected byte %02x in state %i', b, state)

    def getName(self):
        # pylint: disable=unused-variable
        self._write(self._SEQUENCE_GET_NAME)
        unknown = self._readResponse()
        name = self._readResponse()
        return name.decode('ASCII')

    def takeMeasurement(self):
        self._write(self._SEQUENCE_SEND_DATA)
        b = self._readResponse()
        if b is None:
            return None
        return Measurement(b)

    def sendCommand(self, cmd)->None:
        if cmd in self._COMMANDS:
            cmd = self._COMMANDS[cmd]
        if not type(cmd) is int:
            raise Exception(f'bad argument {cmd}')

        seq = self._SEQUENCE_SEND_CMD
        cmd_bytes = bytearray(3)
        cmd_bytes[0] = cmd & 0xff
        cmd = cmd + 379 # don't ask it's from the java source
        cmd_bytes[1] = cmd >> 8
        cmd_bytes[2] = cmd & 0xff
        seq += cmd_bytes
        self._write(seq)
        # pylint: disable=unused-variable
        unknown = self._readResponse()


    def _test(self):
        self._write(self._SEQUENCE_GET_NAME)

        while True:
            x = self.dev.read(64)
            for i in range(1, len(x)):  # skip first byte - length
                hex: str = binascii.hexlify(x[i:i+1]).decode('ASCII')
                c: str = x[i:i+1].decode(encoding='ASCII', errors='ignore')
                if c.isprintable and len(c) == 1:
                    pass
                else:
                    c = '.'
                print(f'{hex} {c}')

