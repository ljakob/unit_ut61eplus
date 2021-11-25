
import logging
from ut61eplus import UT61EPLUS

log = logging.getLogger(__name__)

logging.basicConfig(level=logging.DEBUG)

dmm = UT61EPLUS()

log.info('name=%s', dmm.getName())
dmm.sendCommand('lamp')
m = dmm.takeMeasurement()
log.info('measurent=%s', m)

