import pytest
import re
from .sim_qswitch_fixtures import qswitch  # noqa

@pytest.mark.wip
def test_idn(qswitch):  # noqa
    # -----------------------------------------------------------------------
    idn_dict = qswitch.IDN()
    # -----------------------------------------------------------------------
    assert idn_dict['vendor'] == 'Quantum Machines'
    assert idn_dict['model'] == 'QSwitch'
    assert re.fullmatch('[0-9]+', idn_dict['serial'])
    assert re.fullmatch('[0-9]+\\.[0-9]+', idn_dict['firmware'])


@pytest.mark.wip
def test_abort(qswitch):  # noqa
    # -----------------------------------------------------------------------
    qswitch.abort()
    # -----------------------------------------------------------------------
    commands = qswitch.get_recorded_scpi_commands()
    assert commands == ['abor']


@pytest.mark.wip
def test_reset(qswitch, mocker):  # noqa
    sleep_fn = mocker.patch('qcodes_contrib_drivers.drivers.QDevil.QSwitch.sleep_s')
    # -----------------------------------------------------------------------
    qswitch.reset()
    # -----------------------------------------------------------------------
    commands = qswitch.get_recorded_scpi_commands()
    assert commands == ['*rst']
    sleep_fn.assert_called_once_with(1)
