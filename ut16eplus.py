import binascii
import logging
import hid
from glibc import ctypes

log = logging.getLogger(__name__)

"""
protocol of UT61+

parts from an USB trace, parts from experimenting myself, parts from https://github.com/gulux/Uni-T-CP2110

example response in mV AC

ab . => header
cd . => header
10   => number of bytes that follow including "checksum"
01   => mode
30 0 => range
20   => digit MSB (can be ' ' or '-') ! number can also be ' OL.  '
20   => digit
35 5 => digit
33 3 => digit
2e . => digit
35 5 => digit
34 4 => digit LSB
01   => ?
00   => ?
30 0 => ?
34 4 => ?
30 0 => ?
03   => sum over all - MSB - sum from 0xab to 0x30
8d . => sum over all - LSB

mode:
00 voltage AC (RMS)
01 milli Voltage AC
02 voltage DC
03
04 Hz
05 %
06 resistance
07
08
09
0A
0B
0C micro amps
0D
0E milli amps
0F
10 amps
11
12 hFE
13
14 NCV

range:
30 base unit
36 mega



"""
class Measurement:
    def __init__(self, b : bytes):
        self.b = b


    def __str__(self):
        res = '\n'
        for b in self.b:
            l = '{:02x} {}\n'.format(b, chr(b))
            res += l
        return res
            



class UT16EPLUS:

    CP2110_VID = 0x10c4
    CP2110_PID = 0xEA80

    _SEQUENCE_SEND_DATA = bytes.fromhex('AB CD 03 5E 01 D9')

    def __init__(self):
        self.dev = hid.Device(vid=self.CP2110_VID, pid=self.CP2110_PID)
        #self.dev.nonblocking = 1
        self._send_feature_report([0x41, 0x01]) # enable uart
        self._send_feature_report([0x50, 0x00, 0x00, 0x25, 0x80, 0x00, 0x00, 0x03, 0x00, 0x00]) # 9600 8N1 - from USB trace
        self._send_feature_report([0x43, 0x02]) # purge both fifos

    def _send_init(self):
        self._write(self._SEQUENCE_SEND_DATA)

    def _write(self, b : bytes):
        l = len(b)
        buf = ctypes.create_string_buffer(1 + l)
        buf[0] = l
        buf[1:] = b[0:]
        self.dev.write(buf)

    def _send_feature_report(self, report : bytes):
        l = len(report)
        buf = ctypes.create_string_buffer(l)
        buf[0:l] = report[0:l]
        self.dev.send_feature_report(buf)
    
    def takeMeasurement(self):
        self._send_init()

        state = 0 # 0=init 1=0xAB received 2=0xCD received 3=we have length
        buf : bytes = None
        index : int = None
        sum : int = 0

        while True:
            x = self.dev.read(64)
            b : int
            for b in x[1:]: # skip first byte - length from HID

                if state < 3 or index + 2 < len(buf): # sum all bytes except last 2
                    sum += b

                if   state == 0 and b == 0xAB: state = 1
                elif state == 1 and b == 0xCD: state = 2
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
                        return Measurement(buf[:-2]) # drop last 2 bytes at end
                else:
                    log.warning('unexpected byte %02x in state %i', b, state)


    def test(self):
        self._send_init()

        while True:
            x = self.dev.read(64)
            for i in range(1, len(x)): # skip first byte - length
                hex : str = binascii.hexlify(x[i:i+1]).decode('ASCII')
                c : str = x[i:i+1].decode(encoding='ASCII', errors='ignore')
                if c.isprintable and len(c)== 1:
                    pass
                else:
                    c = '.'
                print(f'{hex} {c}')



