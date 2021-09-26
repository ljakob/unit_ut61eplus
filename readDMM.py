
import logging
from ut16eplus import UT16EPLUS

log = logging.getLogger(__name__)

logging.basicConfig(level=logging.DEBUG)

dmm = UT16EPLUS()

#dmm.test()
m = dmm.takeMeasurement()
log.info('measurent=%s', m)

