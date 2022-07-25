
import logging
from enum import Enum

from ut61eplus import UT61EPLUS
from ut61eplus import SERIAL_NUMBERS

log = logging.getLogger(__name__)

logging.basicConfig(level=logging.DEBUG)

dmm = UT61EPLUS(serial = str(SERIAL_NUMBERS.A))

log.info('name=%s', dmm.getName())
dmm.sendCommand('lamp')
m = dmm.takeMeasurement()
log.info('measurent=%s', m)
dmm.listDevices()
