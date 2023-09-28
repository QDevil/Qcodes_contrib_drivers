import pytest
import uuid
from qcodes_contrib_drivers.drivers.QDevil import QSwitch
import qcodes_contrib_drivers.sims as sims
from qcodes.instrument.base import Instrument

# Use simulated instruments for the tests.
visalib = sims.__file__.replace('__init__.py', 'QSwitch.yaml@sim')


class DUT:
    _instance = None

    @staticmethod
    def instance():
        if not DUT._instance:
            DUT()
        return DUT._instance

    def __init__(self):
        if DUT._instance:
            raise ValueError('DUT is a singleton, use instance() instead')
        DUT._instance = self
        name = ('switch' + str(uuid.uuid4())).replace('-', '')
        try:
            self.switch = QSwitch.QSwitch(name, address='GPIB::4::INSTR', visalib=visalib)
        except Exception as error:
            # Circumvent Instrument not handling exceptions in constructor.
            Instrument._all_instruments.pop(name)
            print(f'CAUGHT: {error}')
            raise

    def __exit__(self):
        self.switch.close()


@pytest.fixture(scope='function')
def qswitch():
    switch = DUT.instance().switch
    switch.start_recording_scpi()
    yield switch
    lingering = switch.clear_read_queue()
    if lingering:
        raise ValueError(f'Lingering messages in visa queue: {lingering}')
